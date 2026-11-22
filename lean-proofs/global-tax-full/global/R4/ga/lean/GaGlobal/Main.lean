import GaGlobal.Model

def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain legacyMain GaGlobal.model args
