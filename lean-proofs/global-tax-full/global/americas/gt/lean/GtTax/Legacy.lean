import GtTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain GtTax.country args
