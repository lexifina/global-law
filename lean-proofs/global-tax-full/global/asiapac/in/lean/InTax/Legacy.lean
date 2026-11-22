import InTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain InTax.country args
