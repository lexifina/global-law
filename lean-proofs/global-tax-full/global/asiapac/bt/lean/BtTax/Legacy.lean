import BtTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BtTax.country args
