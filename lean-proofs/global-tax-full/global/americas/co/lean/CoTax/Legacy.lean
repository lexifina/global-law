import CoTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain CoTax.country args
