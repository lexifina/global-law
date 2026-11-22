import GeTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain GeTax.country args
