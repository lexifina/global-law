import GhTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain GhTax.country args
