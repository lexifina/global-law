import VuTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain VuTax.country args
