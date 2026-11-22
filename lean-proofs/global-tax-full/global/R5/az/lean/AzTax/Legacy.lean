import AzTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain AzTax.country args
