import CnmoGlobal.Model

/-- No 1.x exe exists for CN-MO: legacy mode runs the global model too (each line read as `ofCanon`). -/
def main (args : List String) : IO UInt32 :=
  TaxKernel.Global.globalMain (fun a => TaxKernel.Global.globalRun CnmoGlobal.model ("--global" :: a)) CnmoGlobal.model args
