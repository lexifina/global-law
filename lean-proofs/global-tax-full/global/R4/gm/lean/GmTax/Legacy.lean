import GmTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain GmTax.country args
