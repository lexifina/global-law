import BjTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BjTax.country args
