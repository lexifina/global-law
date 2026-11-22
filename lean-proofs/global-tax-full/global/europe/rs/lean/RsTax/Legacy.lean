import RsTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain RsTax.country args
