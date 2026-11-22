import DjTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain DjTax.country args
