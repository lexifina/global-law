import MhTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain MhTax.country args
