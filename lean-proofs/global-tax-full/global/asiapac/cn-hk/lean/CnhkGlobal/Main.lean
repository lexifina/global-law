import CnhkGlobal.Model

/-- No 1.x exe exists for CN-HK: legacy mode runs the global model too (each line read as `ofCanon`). -/
def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain (fun a => TaxKernel.Global.globalRun CnhkGlobal.model ("--global" :: a)) CnhkGlobal.model args
