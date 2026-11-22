import BaTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BaTax.country args
