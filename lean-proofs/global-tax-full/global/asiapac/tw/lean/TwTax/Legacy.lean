import TwTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain TwTax.country args
