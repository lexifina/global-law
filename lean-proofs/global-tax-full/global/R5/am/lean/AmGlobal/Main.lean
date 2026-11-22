import AmGlobal.Model

def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain legacyMain AmGlobal.model args
