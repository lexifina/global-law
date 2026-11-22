import MxGlobal.Pit

/-!
# Mexico 2025: inheritance (4300) cited not levied; net wealth (4200) grade C

Source: Ley del Impuesto sobre la Renta, Cámara de Diputados text (`mx/law/LISR.pdf`, Wayback capture 2025-06-17,
ARCHIVE_INDEX.tsv). **Art. 93**: "No se pagará el impuesto sobre la renta por la obtención de los siguientes ingresos:
... XXII. Los que se reciban por herencia o legado. XXIII. Los donativos en los siguientes casos: a) Entre cónyuges o
los que perciban los descendientes de sus ascendientes en línea recta, cualquiera que sea su monto ...". The federation
levies no separate inheritance or gift tax: inheritances are outside the ISR (cited not levied, grade A); gifts outside
art. 93 XXIII are ISR income of the donee (taxed through the PIT, not modelled here). No text held on a net wealth tax
(the federal tax laws held, LISR, LIVA, LIEPS, have none): kept grade C.
-/

namespace MxGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon MxGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "inheritances and legacies are exempt from the ISR (LISR art. 93 XXII) and there is no federal inheritance tax; gifts between spouses and lineal relatives exempt (art. 93 XXIII)" },
   { oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 31 fr. IV: \"de la manera proporcional y equitativa que dispongan las leyes\" (`mx/law/const_art-031.md`). no law read in this build levies a recurrent tax on net wealth (laws read include: LIVA arts. 1o, 2o-A, 9, 15, 20; LIEPS art. 2o I A), C), D), G), H); LISR art. 9 (30 %); LISR (DOF 01-04-2024) arts. 140, 164, 156, 166, 167; 1.x model (see its summary.json); LISR arts. 119-121, 124 (DOF 01-04-2024))." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "net wealth tax: no text held (grade C); gifts outside LISR art. 93 XXIII are ISR income of the donee (not modelled here)"


end MxGlobal.Property
