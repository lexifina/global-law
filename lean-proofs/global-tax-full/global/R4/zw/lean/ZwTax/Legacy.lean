import ZwTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain ZwTax.country args
