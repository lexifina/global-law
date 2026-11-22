import BhTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BhTax.country args
