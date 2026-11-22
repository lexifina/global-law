import MeGlobal.Model

/-- `meglobal`: without `--global` exactly the 1.x exe; with `--global` kernel 2.0. -/
def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain legacyMain MeGlobal.model args
