import BrTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BrTax.country args
