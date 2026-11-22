import TaxKernel.Global
import R5Common

/-!
# Yemen 2025: commercial and industrial profits tax on legal persons (1200)

Source: Income Tax Law No. 17 of 2010, English translation by the Tax Authority (`law/itl17_en.pdf`):
art. 63(a): legal persons and non-resident natural persons "at a rate of twenty percent (20%)"; art. 63(e): 35 % on
international telecommunications, cigarette production and import, and the other listed activities (flag
`rate35`). Law No. 8 of 2020 (Sana'a) is not applied: grade B (translation, amendments unchecked).
-/

namespace YeGlobal
open TaxKernel TaxKernel.Global R5Common

def it (co : Company) : CorpRegime :=
  { name := "ضريبة الأرباح التجارية والصناعية", sched := Schedule.flat (if co.flags.contains "rate35" then 3500 else 2000) }

/-- ITL 17/2010 art. 71(a) (Tax Authority English translation, `law/itl17_en.txt`): "Tax at the rate of 10% net of any
deduction shall levy on the amounts paid … to any foreign agency or non-resident person", including interest of foreign
loans (2), royalties (3) and remuneration for services (4); art. 21(f): natural persons' proceeds of shares exempt. -/
def yeWht : Wht :=
  { name := "ضريبة الخصم من المنبع",
    rules := [{ kind := .interest, rateBp := 1000, statute := "ITL 17/2010 art. 71(a)(2) (10 %)" },
              { kind := .royalty, rateBp := 1000, statute := "ITL 17/2010 art. 71(a)(3) (10 %)" },
              { kind := .services, rateBp := 1000, statute := "ITL 17/2010 art. 71(a)(4) (10 %)" },
              WhtRule.zero .dividend "ITL 17/2010 art. 21(f): natural persons' proceeds of shares exempt" (toCompany := some false),
              { kind := .dividend, toCompany := some true, rateBp := 1000, statute := "ITL 17/2010 art. 71(a)(1) (10 % on proceeds paid to a non-resident; art. 5(g)-(h) dividends of resident legal persons are Yemeni-source; art. 21(d) exempts only resident legal persons)" }] }

def corporatePre3q : Family := corpFamily "1200 ضريبة الأرباح" it (fun _ => "ITL 17/2010 art. 63(a) (20 %), 63(e) (35 %)") yeWht

def corporateUnsupportedPre3q (g : CanonGlobal) : List String := corpInputsUnread g true true false true
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest) then ["withholding on interest: loans of international financial institutions or authorized foreign banks exempt (art. 71(a)(2)), not distinguished"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .dividend && p.toCompany) then ["dividends to a foreign company: art. 71(a)(1) 'proceeds' read as covering share proceeds (the English translation uses the word for dividends in art. 21(f)); Arabic text not read (grade B)"] else [])

#guard (it {}).citTax { profit := 1000000 } == 200000
#guard yeWht.amount { kind := .services, amount := 100000 } == 10000
#guard yeWht.amount { kind := .dividend, amount := 100000 } == 10000


/-- Pass 3q year-in-force audit: grade C. 1200 business profits tax grade C (year-in-force audit, pass 3q): the ITL 17/2010 English translation (Law 8/2020 not applied) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied The family above is kept (`corporatePre3q`) for a later re-cite;
it is not in the model. -/
def corporateUnsupported (g : CanonGlobal) : List String :=
  (if (corporatePre3q.run [] g []).isEmpty then [] else ["1200 business profits tax grade C (year-in-force audit, pass 3q): the ITL 17/2010 English translation (Law 8/2020 not applied) is the version read; its 2025 version or amendment history was not reached, so the rule is not applied"]) ++ corporateUnsupportedPre3q g

end YeGlobal
