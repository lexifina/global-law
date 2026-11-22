import TvTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain TvTax.country args
