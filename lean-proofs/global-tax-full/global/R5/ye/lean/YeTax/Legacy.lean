import YeTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain YeTax.country args
