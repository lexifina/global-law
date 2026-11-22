import KeTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain KeTax.country args
