import AuGlobal.Model

def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain (fun a => do legacyMain a; pure 0) AuGlobal.model args
