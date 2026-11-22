import AlTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain AlTax.country args
