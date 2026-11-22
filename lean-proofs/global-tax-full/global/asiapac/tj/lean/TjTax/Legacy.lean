import TjTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain TjTax.country args
