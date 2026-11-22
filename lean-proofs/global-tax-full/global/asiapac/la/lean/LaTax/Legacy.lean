import LaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain LaTax.country args
