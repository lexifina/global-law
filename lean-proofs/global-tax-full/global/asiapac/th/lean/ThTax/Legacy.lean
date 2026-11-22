import ThTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain ThTax.country args
