S = dict(cc="TL", family_name="5126 imposto sobre serviços, 5121 imposto seletivo de consumo",
doc=r'''# Timor-Leste 2025: services tax (5126), excise (5121); no VAT (cited)

Sources (official Jornal da República PDFs on the build server, `cmp20/world/B03-asia-east-se/tl/law/`, sha256 in `law/SOURCES.tsv`):
* **Lei n.º 8/2008 (Lei Tributária)**, JR Série I N.º 26 of 30 June 2008: **art. 5.º** "O imposto sobre serviços incide sobre
  a remuneração bruta … pela prestação de serviços especificados … às taxas estipuladas no Anexo I"; **Anexo I**: monthly
  turnover under US$ 500: 0 %; "igual ou superior a US$ 500: 5%". **Anexo III** imposto sobre vendas: imports 2,5 %;
  "venda de bens tributáveis ou prestação de serviços tributáveis em Timor-Leste: 0%". **Anexo II** excise: "Álcool etílico
  … e outras bebidas alcoólicas US$ 8,90 por litro"; "Gasolina, gasóleo … US$ 0,06 por litro".
* **Lei n.º 8/2024 (Orçamento Geral do Estado para 2025), art. 3.º n.º 4**: "Em 2025, a taxa de imposto seletivo de consumo
  aplicável: a) … bebidas não alcoólicas [sweetened], posição pautal 2202, é de US$ 3 por litro; b) À cerveja de malte com
  teor de álcool inferior a 4,5% … US$ 2,70 por litro; c) À cerveja de malte com outros teores … US$ 4,50 por litro; d) Ao
  vinho … US$ 4,50 por litro; e) Ao tabaco … US$ 50 por quilograma".
Specified services (hotel, restaurant and bar, telecommunications: art. 4.º definitions, not quoted here) are taken as the
basket's `hotels`, `restaurants` and `communication`, by providers above US$ 500 a month. The 2,5 % sales tax on imports
is levied on the customs value at the border, not in the basket (not modelled).''',
extra_lean=r'''def servicesTax (xs : List Spend) : List Charge :=
  (xs.filter fun s => s.good == .hotels || s.good == .restaurants || s.good == .communication).map fun s =>
    charge .goodsOther "Imposto sobre serviços" s.amount id (fun x => divR .down (pos x * 500) BP) (event := s.good.name)
      (bearer := .consumer) (statute := "Lei 8/2008 art. 5.º, Anexo I b) (5 %; turnover ≥ US$ 500 a month)")

/-- Lei 8/2024 art. 3.º n.º 4 b), c): beer below 4,5 % alcohol US$ 2,70 per litre, other beer US$ 4,50. -/
def beerPerL (abvBp : Int) : Int := if abvBp < 450 then 270 else 450

def exciseCharges (xs : List Spend) : List Charge :=
  (xs.filter (·.good == .beer)).map (fun s => charge .excise "Imposto seletivo de consumo (cerveja)" s.quantity id
      (fun q => divR .down (q * beerPerL s.abvBp) 100000) (event := "beer") (bearer := .consumer)
      (statute := "Lei 8/2024 (OGE 2025) art. 3.º n.º 4 b)-c)"))''',
excise=[dict(good="wine", name="Imposto seletivo de consumo (vinho)", num=450, den=100, statute="Lei 8/2024 (OGE 2025) art. 3.º n.º 4 d) (US$ 4,50 por litro)"),
  dict(good="nonAlcoholic", name="Imposto seletivo de consumo (bebidas açucaradas)", num=3, statute="Lei 8/2024 (OGE 2025) art. 3.º n.º 4 a) (US$ 3 por litro)"),
  dict(good="spirits", name="Imposto seletivo de consumo (bebidas alcoólicas)", num=890, den=100, statute="Lei 8/2008 Anexo II (US$ 8,90 por litro)"),
  dict(good="petrol", name="Imposto seletivo de consumo (gasolina)", num=6, den=100, statute="Lei 8/2008 Anexo II (US$ 0,06 por litro)"),
  dict(good="diesel", name="Imposto seletivo de consumo (gasóleo)", num=6, den=100, statute="Lei 8/2008 Anexo II (US$ 0,06 por litro)")],
extra_run=["servicesTax g.consumption","exciseCharges g.consumption"], extra_covers=[".goodsOther"],
absent=[["vat","Lei 8/2008 Anexo III b): no VAT; the sales tax on domestic sales of goods and services is 0 % (imports 2,5 %); a VAT law was in consultation in 2026"]],
notes=["TL 5121/5126: Lei 8/2008 Anexos I-III, Lei 8/2024 (OGE 2025) art. 3.º n.º 4"],
unsupported=[[["cigarettes","tobaccoOther"],"tobacco excise is US$ 50 per kilogram (Lei 8/2024 art. 3.º n.º 4 e)): the basket gives sticks, not weight: not modelled"],
 [["nonAlcoholic"],"the sweetened-drinks rate is applied to all non-alcoholic drinks (fruit and vegetable juices of heading 20.09 are excluded by the law)"],
 ["basket","sales tax of 2,5 % on imports is charged on the customs value at the border: not in the basket"],
 [["spirits","petrol","diesel"],"spirits and fuel rates are the 2008 Anexo II; amendments by Leis 12/2016, 5/2019, 17/2023 to these two rows were not found but not fully read"]],
guards=["excise.duty { good := .wine, amount := 20, quantity := 2000 } == 9","excise.duty { good := .spirits, amount := 30, quantity := 1000, abvBp := 4000 } == 8",
  "(exciseCharges [{ good := .beer, amount := 50, quantity := 10000, abvBp := 400 }]).map (·.due) == [27]",
  "(exciseCharges [{ good := .beer, amount := 50, quantity := 10000, abvBp := 500 }]).map (·.due) == [45]",
  "(servicesTax [{ good := .restaurants, amount := 1000 }]).map (·.due) == [50]"],
taxes=[{"oecd":"5111","tax":"VAT (not levied)","statute":"Lei 8/2008 Anexo III b) (sales tax 0 % on domestic supplies)","dated":"JR 2008; OGE 2025","grade":"A","kernel_parts":["Absent"],"unsupported":[]},
 {"oecd":"5126","tax":"Imposto sobre serviços","statute":"Lei 8/2008 art. 5.º, Anexo I","dated":"JR Série I N.º 26 of 30 June 2008 (rates unchanged in the later amending laws on the build server)","grade":"B","kernel_parts":["charge"],"unsupported":["which services are 'specified' (art. 4.º) taken from the basket classes"]},
 {"oecd":"5121","tax":"Imposto seletivo de consumo (beer, wine, sweetened drinks, spirits, fuel)","statute":"Lei 8/2024 art. 3.º n.º 4 a)-d); Lei 8/2008 Anexo II","dated":"OGE 2025 (JR 26 Nov 2024)","grade":"A","kernel_parts":["Excise","charge"],"unsupported":["tobacco by weight","vehicles (10/20/30 % of value above thresholds)","sales tax 2.5 % on imports"]}])
