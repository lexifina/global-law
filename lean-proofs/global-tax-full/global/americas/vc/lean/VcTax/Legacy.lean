import VcTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain VcTax.country args
