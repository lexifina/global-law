import WsTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain WsTax.country args
