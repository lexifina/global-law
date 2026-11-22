import AmTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain AmTax.country args
