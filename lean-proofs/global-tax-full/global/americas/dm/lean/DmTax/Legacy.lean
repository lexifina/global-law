import DmTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain DmTax.country args
