import PkTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain PkTax.country args
