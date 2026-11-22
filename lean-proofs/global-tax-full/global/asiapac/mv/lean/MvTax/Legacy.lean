import MvTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain MvTax.country args
