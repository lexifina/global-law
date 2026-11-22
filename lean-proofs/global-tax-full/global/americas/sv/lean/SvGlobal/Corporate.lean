import SvGlobal.Pit

/-!
# El Salvador 2025: impuesto sobre la renta de personas jurídicas (1200)

Source: Ley de Impuesto sobre la Renta, D.L. 134 of 18 Dec 1991, Asamblea Legislativa consolidated text with reforms to
(21) D.L. 233 of 14 Dec 2012, hosted by the Superintendencia del Sistema Financiero (`sv/law/ssf_lisr.txt`, fetched
2026-11-21; jurisprudencia.gob.sv and transparencia.mh.gob.sv copies answered 403). Grade B (reforms after 2012 not
read).
* **art. 41**: "LAS PERSONAS JURÍDICAS ... CALCULARÁN SU IMPUESTO APLICANDO A SU RENTA IMPONIBLE LA TASA DEL TREINTA
  POR CIENTO (30%); SE EXCEPTÚAN LOS SUJETOS PASIVOS QUE HAYAN OBTENIDO RENTAS GRAVADAS MENORES O IGUALES A CIENTO
  CINCUENTA MIL DÓLARES (US$150,000), LOS CUALES APLICARÁN LA TASA DEL VEINTICINCO POR CIENTO (25%)" (13) (19).
  Modelled with the kernel small-business schedule on turnover ≤ 150,000 (turnover read as rentas gravadas).
* **art. 72**: profits paid or credited to shareholders: retention "DEL CINCO POR CIENTO (5%)", a final payment
  "SEA ÉSTE DOMICILIADO O NO": modelled as 5 % on dividends paid abroad.
* Not modelled: pago mínimo (arts. 76-81, 1 %), withholding on other payments abroad (Código Tributario art. 158, not
  read).

**Pass 8 (2026-11-21), withholding on payments abroad:** Código Tributario art. 158: a domiciled payer of any El Salvador-source income to a non-domiciled person withholds 20 % as a final payment (inc. 1), including services from abroad used in El Salvador and royalties and other payments for intangibles (inc. 2); reduced rates: 5 % transport, insurance and audiovisual, 10 % financing from qualifying foreign institutions; art. 158-A: 25 % to tax havens. Dividends: LISR art. 72 5 %, final (art. 158 last inc. excludes taxed profits). Grade A (consolidation to 2010; the 2011 and 2015/2026 changes concern other paragraphs).
-/

namespace SvGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon SvGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre la renta (personas jurídicas)", sched := Schedule.flat 3000, smallTurnover := 150000, smallSched := Schedule.flat 2500 }

def citStatute : String := "Ley de Impuesto sobre la Renta (D.L. 134/1991) art. 41 (D.L. 957/2011): 30 %; 25 % when rentas gravadas ≤ US$150,000"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 500, statute := "LISR (D.L. 134/1991) art. 72: 5 % on profits paid to shareholders, domiciled or not, final (Código Tributario art. 158 last inc.: no art. 158 withholding)" }, { kind := .interest, rateBp := 2000, statute := "Código Tributario (D.L. 230/2000) art. 158 inc. 1-2 (D.L. 497/2004, D.L. 233/2009): 20 % final" }, { kind := .royalty, rateBp := 2000, statute := "Código Tributario (D.L. 230/2000) art. 158 inc. 1-2 (D.L. 497/2004, D.L. 233/2009): 20 % final" }, { kind := .services, rateBp := 2000, statute := "Código Tributario (D.L. 230/2000) art. 158 inc. 1-2 (D.L. 497/2004, D.L. 233/2009): 20 % final" }] }

def citF : Family := corpFamily "1200 Impuesto sobre la renta (personas jurídicas)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "pago mínimo (LISR arts. 76-81) not modelled; the US$150,000 test is applied to turnover"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "Código Tributario art. 158 reduced rates (10 % to qualifying foreign financial institutions, 5 % transport, insurance and audiovisual) and art. 158-A (25 % to tax havens) not modelled"

#guard regime.citTax { profit := 1000000, turnover := 5000000 } == 300000
#guard regime.citTax { profit := 100000, turnover := 140000 } == 25000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 50000
#guard wht.amount { kind := .interest, amount := 1000000 } == 200000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 200000
#guard wht.amount { kind := .services, amount := 1000000 } == 200000

end SvGlobal.Corporate
