import TzTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain TzTax.country args
