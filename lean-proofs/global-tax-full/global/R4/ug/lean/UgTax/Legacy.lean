import UgTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain UgTax.country args
