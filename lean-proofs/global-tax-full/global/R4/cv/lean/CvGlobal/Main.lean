import CvGlobal.Model

def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain legacyMain CvGlobal.model args
