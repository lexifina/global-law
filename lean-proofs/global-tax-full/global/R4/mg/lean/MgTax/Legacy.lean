import MgTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain MgTax.country args
