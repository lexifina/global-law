import EtTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain EtTax.country args
