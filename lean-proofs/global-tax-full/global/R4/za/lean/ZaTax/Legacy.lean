import ZaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain ZaTax.country args
