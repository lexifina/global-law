import PsTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain PsTax.country args
