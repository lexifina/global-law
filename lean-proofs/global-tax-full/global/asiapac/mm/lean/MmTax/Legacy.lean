import MmTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain MmTax.country args
