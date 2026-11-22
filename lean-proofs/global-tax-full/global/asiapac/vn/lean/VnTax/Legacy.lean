import VnTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain VnTax.country args
