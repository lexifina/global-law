import SdTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain SdTax.country args
