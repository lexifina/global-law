import BnTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BnTax.country args
