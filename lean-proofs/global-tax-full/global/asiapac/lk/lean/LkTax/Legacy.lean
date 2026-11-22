import LkTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain LkTax.country args
