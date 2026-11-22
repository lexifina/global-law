import TdTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain TdTax.country args
