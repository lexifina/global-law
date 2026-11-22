import MxGlobal.Pit

/-!
# Mexico 2025: IVA (5111) and IEPS (5121)

Sources: Cámara de Diputados PDFs as archived by the Internet Archive in June 2025 (`mx/law/`, ARCHIVE_INDEX.tsv):
LIVA (capture 2025-06-17, "Última Reforma DOF 12-11-2021") and LIEPS (capture 2025-06-18, quotas "actualizada por
acuerdo DOF … 27-12-2024", i.e. the 2025 amounts). Grade A.
* **LIVA art. 1o**: "la tasa del 16%". **art. 2o-A** 0 %: I a) unprocessed animals and vegetables, b) "Medicinas de
  patente y productos destinados a la alimentación" (not prepared food served: restaurants taxed), i) "Libros,
  periódicos y revistas". **art. 15** exempt services: IV education, V urban passenger transport, IX life and
  agricultural insurance, X interest, XIV medical services; **art. 20** II rent of housing.
* **LIEPS art. 2o I**: A) alcoholic drinks and beer up to 14° G.L. 26.5 %, 14-20° 30 %, above 20° 53 %; C) cigarettes
  160 % "Adicionalmente … una cuota de $0.6445 por cigarro"; other tobacco 160 %; D) fuels: gasoline under 91 octane
  6.4555, diesel 7.0946 pesos per litre; G) flavoured drinks with added sugar $1.6451 per litre; H) fossil fuels
  (carbon): gasolines 17.1107, diesel 20.7623 centavos per litre. The ad valorem rates apply to the value of the
  producer's or importer's sale (before IEPS and IVA): read from the consumer price net of both (includes the retail
  margin: an upper bound, flagged).
-/

namespace MxGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon MxGlobal

def vat : Vat :=
  { name := "Impuesto al Valor Agregado", standard := 1600,
    classOf := fun gd => match gd with
      | .food | .medicines | .books | .newspapers | .water => .zero
      | .education | .transport | .insurance | .financial | .health | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "LIVA art. 1o (16 %), 2o-A I a), b), i) (0 %), 15 IV, V, IX, X, XIV, 20 II (exempt)"

def vatF : Family := vatFamily "Impuesto al Valor Agregado" vat vatStatute .vat .central

def lines : List ExLine :=
  [{ good := .beer, name := "IEPS (cerveza)", advBp := 2650, vatBp := 1600, statute := "LIEPS art. 2o I A) 1 (26.5 %)" },
    { good := .wine, name := "IEPS (vino)", advBp := 2650, vatBp := 1600, statute := "LIEPS art. 2o I A) 1 (26.5 %, up to 14° G.L.)" },
    { good := .spirits, name := "IEPS (bebidas alcohólicas)", advBp := 5300, vatBp := 1600, statute := "LIEPS art. 2o I A) 3 (53 %)" },
    { good := .cigarettes, name := "IEPS (cigarros)", num := 6445, den := 10000, advBp := 16000, vatBp := 1600, statute := "LIEPS art. 2o I C) 1 (160 % + $0.6445 per cigarette, DOF 27-12-2024)" },
    { good := .tobaccoOther, name := "IEPS (puros y otros tabacos)", advBp := 16000, vatBp := 1600, statute := "LIEPS art. 2o I C) 2 (160 %)" },
    { good := .nonAlcoholic, name := "IEPS (bebidas saborizadas)", num := 16451, den := 10000, statute := "LIEPS art. 2o I G) ($1.6451 per litre)" },
    { good := .petrol, name := "IEPS (gasolina + combustibles fósiles)", num := 6626607, den := 1000000, statute := "LIEPS art. 2o I D) 1 a. (6.4555 per litre) + H) 3 (17.1107 centavos per litre)" },
    { good := .diesel, name := "IEPS (diésel + combustibles fósiles)", num := 7302223, den := 1000000, statute := "LIEPS art. 2o I D) 1 c. (7.0946 per litre) + H) 5 (20.7623 centavos per litre)" }]

def exciseF : Family :=
  { name := "5121 excises", covers := [.excise],
    run := fun _ g _ => exciseCharges lines g.consumption }

def families : List Family := [vatF, exciseF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 31 fr. IV: \"de la manera proporcional y equitativa que dispongan las leyes\" (`mx/law/const_art-031.md`). LIVA art. 41 fr. I (held `mx/law/LIVA.txt`): states in the Sistema Nacional de Coordinación Fiscal agree 'en no mantener impuestos locales o municipales sobre ... Los actos o actividades por los que deba pagarse el impuesto al valor agregado' (lodging excepted); no law read in this build levies a general sales or turnover tax beside the VAT of the 5111 row (laws read include: LIVA arts. 1o, 2o-A, 9, 15, 20; LIEPS art. 2o I A), C), D), G), H); LISR art. 9 (30 %); LISR (DOF 01-04-2024) arts. 140, 164, 156, 166, 167; 1.x model (see its summary.json); LISR arts. 119-121, 124 (DOF 01-04-2024))." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .petrol || s.good == .diesel) "fuel IEPS: the statutory quota is charged; the weekly fiscal-stimulus decrees (DOF) that reduce it in 2025 are not modelled (upper bound)"
  ++ when (g.consumption.any fun s => s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic) "IEPS by alcoholic strength read per good (wine ≤ 14°, spirits > 20°); flavoured drinks taken as containing added sugar"
  ++ when (g.consumption.any fun s => s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .cigarettes || s.good == .tobaccoOther) "IEPS ad valorem base read from the consumer price net of IVA and IEPS (statute: the producer's or importer's sale value): upper bound"
  ++ when (!g.consumption.isEmpty) "ISN, predial and other CDMX taxes are not inside the basket model"

#guard vat.embedded { good := .clothing, amount := 1160 } == 160
#guard vat.embedded { good := .food, amount := 1160 } == 0
-- 20 cigarettes: $0.6445 each = 12.89, plus 160 % of the price before IEPS and IVA
#guard (lines.find? (·.good == .cigarettes)).get!.specific { good := .cigarettes, amount := 100, quantity := 20000 } == 12
#guard (lines.find? (·.good == .petrol)).get!.duty { good := .petrol, amount := 2400, quantity := 100000 } == 662

end MxGlobal.Consumption
