import SgTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain SgTax.country args
