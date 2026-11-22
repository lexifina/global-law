import BbTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BbTax.country args
