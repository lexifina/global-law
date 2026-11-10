/**
 * Run UsTaxes (github.com/ustaxes/UsTaxes, tax year 2025 forms) on the households from gen_households.py.
 *
 *   node C:/Users/alany/Documents/tax-formalization-data/ustaxes-runner/run.mjs households.json ustaxes.json [flags]
 *
 * run.mjs bundles this file with esbuild (alias `ustaxes/*` -> the UsTaxes clone's src/*, npm deps from
 * ustaxes-runner/node_modules; nothing is installed into or changed in the clone) and then runs the bundle.
 * One-time setup: `cd ustaxes-runner && npm install --ignore-scripts` (esbuild, lodash, pdf-lib, date-fns).
 *
 * Output: one object per household, in input order, with agi (F1040 l11), taxableIncome (l15), taxBeforeCredits (l18 =
 * l16 + Schedule 2 AMT), eitc (l27), ctc (Schedule 8812 l14 = nonrefundable CTC+ODC on l19), actc (l28), cdcc (Form
 * 2441 credit before the liability limit), incomeTax (l22 + NIIT - eitc - actc), seTax (Schedule SE l12), niit (Form
 * 8960 l17), qbid (l13a); or {"error": "..."}.
 *
 * Two workarounds for UsTaxes 2025 gaps are on by default (each can be turned off):
 *   --no-schedc-fix  UsTaxes' Y2025 F1040 constructor never creates `scheduleC`, so Information.selfEmployedIncome is
 *                    silently ignored (no Schedule 1 line 3, no SE tax). The runner attaches `new ScheduleC(f1040)`
 *                    before any line is evaluated (all lines are lazy), which is what the constructor should do.
 *                    The constructor picks Form 8995 vs 8995-A from l11b - l12e before that attach, so the runner
 *                    repeats the constructor's own choice afterwards (same rule, now with Schedule C income).
 *   --no-qbi-shim    UsTaxes computes the §199A deduction only from K-1 box 20Z (F1040.totalQbi); Schedule C profit is
 *                    never QBI. The runner enters the sole proprietorship's QBI (net profit - deductible half of SE
 *                    tax, from a first pass) as a K-1 with every other field zero, the way a user would.
 * One opt-in patch, for diagnosis only (off by default, so the output is UsTaxes' own answer):
 *   --patch-sched3   Schedule3.isNeeded ignores Form 2441, so the dependent care credit never reaches F1040 l20 or
 *                    Credit Limit Worksheet A; this forces Schedule 3 on.
 */
import {
  FilingStatus,
  Income1099Type,
  Information,
  PersonRole,
  PlanType1099,
  Dependent,
  ScheduleK1Form1065
} from 'ustaxes/core/data'
import { validate } from 'ustaxes/forms/F1040Base'
import F1040 from 'ustaxes/forms/Y2025/irsForms/F1040'
import ScheduleC from 'ustaxes/forms/Y2025/irsForms/ScheduleC'
import F8995, { getF8995PhaseOutIncome } from 'ustaxes/forms/Y2025/irsForms/F8995'
import F8995A from 'ustaxes/forms/Y2025/irsForms/F8995A'
import * as fs from 'fs'

/* eslint-disable @typescript-eslint/no-explicit-any */
type H = any

const args = process.argv.slice(2).filter((a) => !a.startsWith('--'))
const flags = new Set(process.argv.slice(2).filter((a) => a.startsWith('--')))
const SCHEDC_FIX = !flags.has('--no-schedc-fix')
const QBI_SHIM = !flags.has('--no-qbi-shim')
const PATCH_SCHED3 = flags.has('--patch-sched3')
const MEMO = !flags.has('--no-memo')

const YEAR = 2025
// Age at the end of 2025; a mid-year birthday keeps the 65+ test (born before 2 Jan 1961) and birth-year tests exact.
const dob = (age: number): Date => new Date(YEAR - age, 6, 1)
const addr = { address: '1 Main St', city: 'Austin', state: 'TX' as const, zip: '78701' }

const w2 = (income: number, role: PersonRole.PRIMARY | PersonRole.SPOUSE) => ({
  occupation: 'worker', income, medicareIncome: income, ssWages: income, fedWithholding: 0, ssWithholding: 0,
  medicareWithholding: 0, personRole: role, state: 'TX' as const, stateWages: income, stateWithholding: 0
})

function information(h: H, qbi: number): Information {
  const status = { single: FilingStatus.S, mfj: FilingStatus.MFJ, hoh: FilingStatus.HOH, mfs: FilingStatus.MFS }[
    h.filing as string]
  if (status === undefined) throw new Error(`unsupported filing status ${h.filing}`)
  const P = PersonRole.PRIMARY
  const deps: Dependent[] = (h.dependents as H[]).map((d, i) => ({
    firstName: `Dep${i}`, lastName: 'Test', ssid: String(400000010 + i), role: PersonRole.DEPENDENT,
    isBlind: false, dateOfBirth: dob(d.age), relationship: 'Child',
    qualifyingInfo: { numberOfMonths: d.monthsWithTaxpayer ?? 12, isStudent: !!d.student }
  }))
  const headWages = h.wages - h.wagesSpouse
  const w2s = []
  if (headWages > 0) w2s.push(w2(headWages, P))
  if (h.wagesSpouse > 0) w2s.push(w2(h.wagesSpouse, PersonRole.SPOUSE))

  const f1099s: any[] = []
  if (h.taxableInterest) f1099s.push({ payer: 'Bank', type: Income1099Type.INT, personRole: P, form: { income: h.taxableInterest } })
  if (h.ordinaryDividends)
    f1099s.push({ payer: 'Fund', type: Income1099Type.DIV, personRole: P,
      form: { dividends: h.ordinaryDividends, qualifiedDividends: h.qualifiedDividends, totalCapitalGainsDistributions: 0 } })
  if (h.shortTermGains || h.longTermGains)
    f1099s.push({ payer: 'Broker', type: Income1099Type.B, personRole: P,
      form: { shortTermProceeds: h.shortTermGains, shortTermCostBasis: 0, longTermProceeds: h.longTermGains, longTermCostBasis: 0 } })
  if (h.pensions)
    f1099s.push({ payer: 'Plan', type: Income1099Type.R, personRole: P,
      form: { grossDistribution: h.pensions, taxableAmount: h.pensions, federalIncomeTaxWithheld: 0, planType: PlanType1099.Pension } })
  if (h.socialSecurity)
    f1099s.push({ payer: 'SSA', type: Income1099Type.SSA, personRole: P, form: { netBenefits: h.socialSecurity, federalIncomeTaxWithheld: 0 } })

  const itemizing = h.stateLocalTaxes || h.mortgageInterest || h.charitableCash || h.medicalExpenses
  const k1s: ScheduleK1Form1065[] = qbi > 0 ? [{
    personRole: P, partnershipName: 'Schedule C QBI (runner shim)', partnershipEin: '000000000', partnerOrSCorp: 'P',
    isForeign: false, isPassive: false, ordinaryBusinessIncome: 0, interestIncome: 0, guaranteedPaymentsForServices: 0,
    guaranteedPaymentsForCapital: 0, selfEmploymentEarningsA: 0, selfEmploymentEarningsB: 0, selfEmploymentEarningsC: 0,
    distributionsCodeAAmount: 0, section199AQBI: qbi
  }] : []
  const under13 = (h.dependents as H[]).filter((d) => d.age < 13).length

  return {
    f1099s, w2s, realEstate: [], estimatedTaxes: [], f1098es: [], f3921s: [], scheduleK1Form1065s: k1s,
    itemizedDeductions: itemizing ? {
      medicalAndDental: h.medicalExpenses, stateAndLocalTaxes: 0, isSalesTax: false,
      stateAndLocalRealEstateTaxes: h.stateLocalTaxes, stateAndLocalPropertyTaxes: 0, interest8a: h.mortgageInterest,
      interest8b: 0, interest8c: 0, interest8d: 0, investmentInterest: 0, charityCashCheck: h.charitableCash, charityOther: 0
    } : undefined,
    taxPayer: {
      filingStatus: status,
      primaryPerson: { firstName: 'Head', lastName: 'Test', ssid: '400000001', role: P, isBlind: !!h.head.blind,
        dateOfBirth: dob(h.head.age), address: addr, isTaxpayerDependent: !!h.canBeClaimedAsDependent },
      spouse: h.spouse ? { firstName: 'Spouse', lastName: 'Test', ssid: '400000002', role: PersonRole.SPOUSE,
        isBlind: !!h.spouse.blind, dateOfBirth: dob(h.spouse.age), isTaxpayerDependent: false } : undefined,
      dependents: deps
    },
    questions: {}, credits: [], stateResidencies: [{ state: 'TX' }], healthSavingsAccounts: [],
    individualRetirementArrangements: [],
    selfEmployedIncome: h.seIncome ? [{ businessName: 'Sole prop', personRole: P, grossReceipts: h.seIncome, expenses: 0 }] : [],
    otherIncome: h.unemployment ? { unemploymentCompensation: h.unemployment } : undefined,
    dependentCareExpenses: h.childCareExpenses && under13 > 0
      ? { qualifyingPersonCount: under13, totalExpenses: h.childCareExpenses } : undefined
  } as Information
}

function build(h: H, qbi: number): F1040 {
  // Main.ts create1040 = validate + new F1040 + f1040.schedules(); the last only lists attachments for PDF output and
  // evaluates the whole return once more without caching, so it is skipped here.
  const r: any = validate(information(h, qbi))
  if (r._tag === 'left') throw new Error(`validation: ${JSON.stringify(r.left)}`)
  const f = new F1040(r.right, [])
  if (SCHEDC_FIX && f.scheduleC === undefined && (f.info.selfEmployedIncome ?? []).length > 0) {
    f.scheduleC = new ScheduleC(f)
    if (f.totalQbi() > 0) {  // same rule as the F1040 constructor
      const formA = f.l11b() - f.l12e() >= getF8995PhaseOutIncome(f.info.taxPayer.filingStatus)
      f.f8995 = formA ? new F8995A(f) : new F8995(f)
    }
  }
  if (PATCH_SCHED3) f.schedule3.isNeeded = () => true
  if (MEMO) memoize(f)
  return f
}

/**
 * UsTaxes lines are uncached arrow functions that re-evaluate their whole dependency tree on every call (~100-300 ms
 * per household). The inputs are fixed once the forms exist, so cache every zero-argument method of F1040 and of each
 * form attached to it. Results are identical (check with --no-memo); only the run time changes.
 */
function memoize(f: F1040): void {
  const forms = [f, ...Object.values(f).filter((v: any) => v && typeof v === 'object' && v.f1040 === f)]
  for (const form of forms as any[]) {
    for (const k of Object.keys(form)) {
      const fn = form[k]
      if (typeof fn !== 'function' || fn.length !== 0) continue
      let done = false, value: unknown
      form[k] = (...a: unknown[]) => {
        if (a.length) return fn(...a)
        if (!done) { value = fn(); done = true }
        return value
      }
    }
  }
}

const n = (x: number | undefined): number => x ?? 0

function run(h: H) {
  let f = build(h, 0)
  if (QBI_SHIM && SCHEDC_FIX && h.seIncome > 0) {
    const qbi = n(f.scheduleC?.l31()) - n(f.schedule1.l15())
    if (qbi > 0) f = build(h, qbi)
  }
  const eitc = f.l27a(), actc = n(f.l28()), niit = n(f.f8960.l17())
  return {
    agi: f.l11a(), taxableIncome: f.l15(), taxBeforeCredits: f.l18(), eitc, ctc: n(f.l19()), actc,
    cdcc: n(f.f2441.credit()), incomeTax: f.l22() + niit - eitc - actc, seTax: n(f.scheduleSE.l12()), niit,
    qbid: n(f.l13a()), amt: n(f.l17())
  }
}

if (args.length < 2) {
  console.error('usage: run.mjs households.json out.json [--no-schedc-fix] [--no-qbi-shim] [--patch-sched3] [--no-memo]')
  process.exit(2)
}
const hs: H[] = JSON.parse(fs.readFileSync(args[0], 'utf-8'))
const t0 = Date.now()
const out = hs.map((h) => {
  try {
    return run(h)
  } catch (e: any) {
    return { error: String(e?.message ?? e).slice(0, 300) }
  }
})
fs.writeFileSync(args[1], JSON.stringify(out))
const errors = out.filter((r: any) => 'error' in r).length
console.log(`done ${out.length} households, ${errors} errors, ${Date.now() - t0} ms` +
  ` (schedc-fix ${SCHEDC_FIX ? 'on' : 'off'}, qbi-shim ${QBI_SHIM ? 'on' : 'off'}, patch-sched3 ${PATCH_SCHED3 ? 'on' : 'off'})`)
