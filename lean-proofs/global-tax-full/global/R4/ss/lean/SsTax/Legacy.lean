import SsTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain SsTax.country args
