import MrTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain MrTax.country args
