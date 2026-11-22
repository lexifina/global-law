import ArTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain ArTax.country args
