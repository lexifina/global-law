import SrTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain SrTax.country args
