import PaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain PaTax.country args
