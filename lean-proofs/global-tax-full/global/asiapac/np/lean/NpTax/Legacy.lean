import NpTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain NpTax.country args
