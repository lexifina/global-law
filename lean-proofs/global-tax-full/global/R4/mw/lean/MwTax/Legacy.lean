import MwTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain MwTax.country args
