import ClGlobal.Model

/-- `clglobal`: without `--global` exactly the 1.x `cltax`; with `--global` the kernel-2.0 output (all families). -/
def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain (TaxKernel.worldMain ClTax.country) ClGlobal.model args
