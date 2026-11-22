import SoTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain SoTax.country args
