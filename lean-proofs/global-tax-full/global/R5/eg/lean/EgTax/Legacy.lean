import EgTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain EgTax.country args
