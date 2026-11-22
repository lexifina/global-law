import BfTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BfTax.country args
