import VeGlobal.Pit

/-!
# Venezuela 2025: Impuesto al Valor Agregado (5111); excises grade C

Source: Decreto Constituyente de Reforma Parcial del Decreto con Rango, Valor y Fuerza de Ley que Establece el Impuesto
al Valor Agregado, G.O. 6.507 Ext. of 29 Jan 2020, with the reprinted law in the same gazette (`ve/law/go6507ext_2020.pdf`,
reprint extracted to `ve/law/go6507ext_ley_iva_reprint.txt`). Grade A.
* **Art. 27**: general rate fixed by the Executive between 8 % and 16.5 %; additional 15-20 % on luxury goods and services
  (art. 61) and 5-25 % on supplies paid in foreign currency (art. 62).
* **Art. 63** (transitional): "la alícuota impositiva general ... será del dieciséis por ciento (16%), hasta tanto el
  Ejecutivo Nacional establezca una alícuota distinta". **Art. 64**: 8 % on some meats (other than those of art. 18),
  lard, domestic air passenger transport.
* **Art. 18** exempt goods: 1. the listed basic foods (vegetables in their natural state, rice, flour, bread and pasta,
  eggs, salt, sugar, coffee, milk, cheese, margarine, chicken, beef and pork, oils ...); 3. medicines; 5. newspapers; 6.
  books. **Art. 19** exempt services: 1. domestic land and water passenger transport; 3. education; 6. medical and dental
  services; 9. residential electricity; 11. residential water; 13. residential gas. **Art. 16** not subject: 4. banking
  and financial services; 5. insurance.
Mapping: food exempt (the art. 18 list covers the staples; processed food outside it pays 16 %: lower bound), medicines,
books, newspapers, electricity, water, gas, transport, education, health exempt; financial and insurance not subject;
everything else 16 %, including house rent (no exemption for dwellings in arts. 16-19; a landlord who is not an
ordinary taxpayer charges none: upper bound). Not applied: the art. 61 luxury surcharge, the art. 62 foreign-currency
rate (its decree not read), the 8 % of art. 64, the IGTF. No later decree changing the 16 % was checked.
-/

namespace VeGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon VeGlobal

def vat : Vat :=
  { name := "Impuesto al Valor Agregado", standard := 1600,
    classOf := fun gd => match gd with
      | .food | .medicines | .books | .newspapers | .electricity | .water | .gas | .transport | .education | .health | .financial | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "Ley IVA (reprint, G.O. 6.507 Ext., 29 Jan 2020) art. 63 (16 %), art. 18 nos. 1, 3, 5, 6, art. 19 nos. 1, 3, 6, 9, 11, 13 (exempt), art. 16 nos. 4, 5 (not subject)"

def vatF : Family := vatFamily "Impuesto al Valor Agregado" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food taken as exempt (art. 18 no. 1 lists the staples); food outside the list pays 16 % (8 % for some meats, art. 64): lower bound"
  ++ when (g.consumption.any fun s => s.good == .rent) "house rent taxed at 16 % (no exemption in arts. 16-19); landlords who are not ordinary taxpayers charge none: upper bound"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) "excises on alcohol, tobacco and fuel not modelled"
  ++ when (!g.consumption.isEmpty) "luxury surcharge (art. 61), foreign-currency surcharge (art. 62) and IGTF not applied"

#guard vat.embedded { good := .clothing, amount := 1160 } == 160
#guard vat.embedded { good := .food, amount := 1160 } == 0
#guard vat.embedded { good := .rent, amount := 1160 } == 160
#guard vat.embedded { good := .electricity, amount := 1160 } == 0

end VeGlobal.Consumption
