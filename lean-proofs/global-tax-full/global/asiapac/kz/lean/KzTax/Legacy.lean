import KzTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain KzTax.country args
