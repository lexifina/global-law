import TnTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain TnTax.country args
