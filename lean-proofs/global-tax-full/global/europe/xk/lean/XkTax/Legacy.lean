import XkTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain XkTax.country args
