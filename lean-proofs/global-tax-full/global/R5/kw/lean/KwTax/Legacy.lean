import KwTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain KwTax.country args
