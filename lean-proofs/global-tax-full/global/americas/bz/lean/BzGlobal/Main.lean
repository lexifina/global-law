import BzGlobal.Model

def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain legacyMain BzGlobal.model args
