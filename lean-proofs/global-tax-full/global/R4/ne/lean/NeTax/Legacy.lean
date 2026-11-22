import NeTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain NeTax.country args
