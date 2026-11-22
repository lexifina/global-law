S = dict(cc="CR", fam="Consumption",
doc=r'''# Costa Rica 2025: Impuesto sobre el Valor Agregado (5111); selective and fuel taxes grade C

Source: Ley 6826, Ley de Impuesto al Valor Agregado (texto del Título I de la Ley 9635), SINALEVI (PGR) consolidated
text, ficha 32526, versión 31 de 31 (id 150649), fetched 2026-11-21 from the SINALEVI endpoint
`/ResultadosNormativa/_CargarTextoCompleto` (`cr/law/iva_ley6826_sinalevi_v150649.json`, ARCHIVE_INDEX.tsv). The reform
notes in the text run to Ley 10712 of 7 April 2026, which only adds art. 9 inc. 13 (breast-cancer screening, outside the
modelled goods); Leyes 10479, 10512, 10579 (2024) precede 2025. Grade A.
* **Art. 10**: "La tarifa del impuesto es del trece por ciento (13%)".
* **Art. 11**: 4 % on (1 a) domestic air tickets and (1 b) "Los servicios de salud privados"; 2 % on (2 a) "Los
  medicamentos", (2 b) private education (Ley 10479 of 2024), (2 c) "Las primas de seguros personales"; 1 % on (3 b) the
  canasta básica goods.
* **Art. 8 (exempt)**: inc. 3 interest and commissions on loans and credit; inc. 9 rent of dwellings where the monthly
  rent is at most 1.5 salario base (above that, on the whole rent); inc. 11 "El suministro de energía eléctrica
  residencial, siempre que el consumo mensual sea igual o inferior a 280 kW/h"; inc. 12 residential water up to 30 m3;
  inc. 24 regulated land passenger transport; inc. 25 "Los libros con independencia de su formato".
* **Art. 9 inc. 12 (no sujeción)**: fuels taxed under Ley 8114 chapter I (impuesto único a los combustibles).
* Food read as the canasta básica (1 %; other food 13 %: lower bound, flagged); education read as private (2 %; public
  education is exempt under art. 8 inc. 31: upper bound); the electricity, water and rent caps are not modelled.''',
vat=dict(name="Impuesto sobre el Valor Agregado", standard=1300, reduced=400, reduced2=200, superReduced=100,
  statute="Ley 6826 (texto Ley 9635) art. 10 (13 %), art. 11 (4 %, 2 %, 1 %), art. 8 inc. 3, 9, 11, 12, 24, 25 (exempt), art. 9 inc. 12 (fuel not subject); SINALEVI versión 31",
  classes={"food":"superReduced","health":"reduced","medicines":"reduced2","education":"reduced2","insurance":"reduced2",
           "financial":"exempt","rent":"exempt","electricity":"exempt","water":"exempt","transport":"exempt","books":"exempt",
           "petrol":"exempt","diesel":"exempt"}),
unsupported=[["g.consumption.any fun s => s.good == .food", "food read as canasta básica goods at 1 % (art. 11 (3 b)); food outside the canasta is taxed at 13 % (lower bound)"],
 ["g.consumption.any fun s => s.good == .electricity || s.good == .water || s.good == .rent", "residential electricity up to 280 kWh, water up to 30 m3 and rent up to 1.5 salario base a month are exempt; above those caps the whole amount is taxed at 13 %: read as within the caps (lower bound)"],
 ["g.consumption.any fun s => s.good == .education", "education read as private (2 %); public education is exempt (art. 8 inc. 31)"],
 ["g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel", "selective consumption taxes and the impuesto único a los combustibles (Ley 8114) not modelled"]],
guards=["vat.embedded { good := .clothing, amount := 1130 } == 130", "vat.embedded { good := .health, amount := 1040 } == 40",
        "vat.embedded { good := .medicines, amount := 1020 } == 20", "vat.embedded { good := .food, amount := 1010 } == 10",
        "vat.embedded { good := .petrol, amount := 1130 } == 0"],
taxes=[dict(oecd="5111", tax="Impuesto sobre el Valor Agregado", statute="Ley 6826 (texto Ley 9635) arts. 8, 9, 10, 11", dated="SINALEVI consolidated text versión 31 (reforms to Ley 10712 of 7 April 2026, which does not touch the modelled goods)", grade="A", package="P1", kernel_parts=["Vat"], unsupported=["consumption caps on electricity, water and rent", "canasta básica coverage of food"]),
 dict(oecd="5121", tax="Impuestos selectivos de consumo, único a los combustibles, bebidas y tabaco", statute="Ley 4961; Ley 8114; Ley 7972; Ley 9028", grade="C", status="unsupported", package="P1", kernel_parts=[], tried="not attempted (amounts indexed by decree)", unsupported=["would unlock: the 2025 decrees updating the fuel and selective amounts"])])
