import MeTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain MeTax.country args
