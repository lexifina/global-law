import GnTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain GnTax.country args
