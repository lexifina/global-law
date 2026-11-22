S = dict(cc="BO", fam="Consumption",
doc=r'''# Bolivia 2025: IVA (5111) and ICE / IEHD (5121)

Source: Ley N° 843, Texto Ordenado, Complementado y Actualizado al 30 de septiembre de 2023 (SIN,
`world/B12-latin-america/bo/src/l843_0923.txt`; the newest consolidation reached; 2024-2025 amendments not checked:
grade B).
* **art. 15**: "La alícuota general única del impuesto será del 13% (trece por ciento)". **art. 5**: the base is the
  price "consignado en la factura"; the tax is inside the invoiced price ("cuya carga tributaria es trasladada al
  comprador dentro del precio de venta", Disposiciones Relacionadas to the IVA title): the IVA in a consumer amount is
  13 % of it, and on a supply invoiced at `net` before tax it is 13/87 of `net`.
* **art. 14**: exemptions are only imports by diplomats and travellers' bona fide goods: every basket good is taxed.
* **ICE, art. 79 and Anexo**: Tabla 1 "Los demás tabacos … 50%"; the specific rates (cigarettes Bs139 per 1.000 and
  the beverage table) "se actualizarán por la Administración Tributaria para cada gestión en base a la variación de la
  UFV" (RND, not read): unsupported. **IEHD** (Título IX): "una tasa máxima de Bs3.50 por litro", the rates set by
  decree: unsupported.''',
lean=r'''
/-- 13 % of the tax-inclusive price (art. 5, 15). -/
def ivaIn (amount : Int) : Int := divR .down (1300 * pos amount) BP
/-- 13 % of a price whose net-of-tax part is `net`: 13/87 of `net`. -/
def ivaOnNet (net : Int) : Int := divR .down (1300 * pos net) 8700

def vatF : Family :=
  { name := "5111 IVA", covers := [.vat],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [charge .vat "Impuesto al Valor Agregado" (isum (g.consumption.map (·.amount))) id
          (fun _ => isum (g.consumption.map fun s => ivaIn s.amount)) (event := "basket") (bearer := .consumer)
          (statute := "Ley 843 art. 5, 15 (13 % inside the price), art. 14")])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
        [charge .vat "Impuesto al Valor Agregado" (isum (g.company.sales.map (·.net))) id
          (fun _ => isum (g.company.sales.map fun s => if s.exported then 0 else ivaOnNet s.net)
                    - isum (g.company.inputs.map fun s => ivaOnNet s.net))
          (event := "supplies") (bearer := .consumer) (statute := "Ley 843 art. 7, 8 (débito − crédito fiscal), 15")] else []) }
''',
ex=[dict(good="tobaccoOther", name="Impuesto a los Consumos Específicos (demás tabacos)", adv=5000, vat=1494,
         statute="Ley 843 art. 79, Anexo Tabla 1 (50 %)")],
families="[vatF, exciseF]",
unsupported=[["g.consumption.any fun s => s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic",
  "ICE specific rates (cigarettes, beverages) are updated each year by RND on the UFV (Ley 843 Anexo art. 79): 2025 RND not read; not charged"],
 ["g.consumption.any fun s => s.good == .petrol || s.good == .diesel", "IEHD (Ley 843 Título IX): rates set by supreme decree up to Bs3.50/l; not read; not charged"],
 ["g.consumption.any (·.good == .tobaccoOther)", "ICE 50 % base taken as the consumer price net of IVA and of the ICE itself (ICE base: the producer's sale price)"]],
guards=["ivaIn 1000 == 130", "ivaOnNet 870 == 130",
        "(lines.head!).duty { good := .tobaccoOther, amount := 1725 } == 500"],
taxes=[dict(oecd="5111", tax="Impuesto al Valor Agregado", statute="Ley 843 arts. 5, 7, 8, 14, 15", dated="T.O. actualizado al 30/09/2023 (SIN); 2025 amendments not checked", grade="B", package="P1", kernel_parts=["charge"], unsupported=["exemptions in special laws outside Ley 843 not read"]),
 dict(oecd="5121", tax="ICE (demás tabacos)", statute="Ley 843 art. 79 Anexo Tabla 1", dated="T.O. 30/09/2023", grade="B", package="P1", kernel_parts=["ExLine"], unsupported=["base approximated from the consumer price"]),
 dict(oecd="5121", tax="ICE (cigarrillos, bebidas)", statute="Ley 843 art. 79 Anexo; annual RND", grade="C", status="unsupported", package="P1", unsupported=["specific rates indexed to the UFV each gestión by RND; would unlock: the RND fixing the 2025 rates"]),
 dict(oecd="5121", tax="IEHD (hidrocarburos)", statute="Ley 843 Título IX; supreme decrees", grade="C", status="unsupported", package="P1", unsupported=["rates set by decree (max Bs3.50/l); would unlock: the D.S. in force in 2025"])])
