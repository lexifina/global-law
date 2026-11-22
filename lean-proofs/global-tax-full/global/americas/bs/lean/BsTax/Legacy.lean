import BsTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BsTax.country args
