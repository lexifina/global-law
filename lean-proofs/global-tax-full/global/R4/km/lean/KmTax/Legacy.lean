import KmTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain KmTax.country args
