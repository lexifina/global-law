import PwTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain PwTax.country args
