import BwTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BwTax.country args
