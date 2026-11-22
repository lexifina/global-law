import GdTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain GdTax.country args
