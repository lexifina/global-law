import VeTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain VeTax.country args
