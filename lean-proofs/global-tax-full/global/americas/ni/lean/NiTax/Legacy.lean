import NiTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain NiTax.country args
