import KeGlobal.Model

def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain legacyMain KeGlobal.model args
