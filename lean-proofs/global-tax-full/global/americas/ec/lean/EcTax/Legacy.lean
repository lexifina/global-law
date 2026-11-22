import EcTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain EcTax.country args
