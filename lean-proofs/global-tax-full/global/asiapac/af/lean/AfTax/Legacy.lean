import AfTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain AfTax.country args
