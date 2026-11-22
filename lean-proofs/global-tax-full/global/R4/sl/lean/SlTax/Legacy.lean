import SlTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain SlTax.country args
