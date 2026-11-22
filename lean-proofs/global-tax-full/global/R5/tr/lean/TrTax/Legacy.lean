import TrTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain TrTax.country args
