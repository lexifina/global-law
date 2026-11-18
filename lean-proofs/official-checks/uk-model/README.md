# UK income tax and National Insurance, 2025-26, in Lean

A model of the UK income tax (ITA 2007, ITEPA 2003, including s. 681C) and Class 1 National Insurance for one
person, written from the statute provision by provision, in Lean 4 core (v4.35.0). `lake build` builds the library
and the `uktax` executable the checks call; `UkTax/Theorems.lean` holds the proved properties, `UkTax/Checks.lean` the
checks against figures HMRC and GOV.UK publish, and `PAYETestData.lean` and `NITestData.lean` HMRC's payroll test
data.

`HOWWRITTEN.md` explains how it was written, `EXAMPLE.md` walks through one household, and `harness/` has the scripts
that fetched the law and guidance and compared the model with PolicyEngine-UK and the OECD.

The scripts were run on our build machine, where the checkouts and tools sat under `~/cmp`; the paths at the top of each script say where they expect them.
