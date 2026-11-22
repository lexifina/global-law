import BdTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BdTax.country args
