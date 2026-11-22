import CyGlobal.Model

/-- `cyglobal`: without `--global` exactly the 1.x `cytax` (its `main`, renamed); with `--global` kernel 2.0. -/
def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain legacyMain CyGlobal.model args
