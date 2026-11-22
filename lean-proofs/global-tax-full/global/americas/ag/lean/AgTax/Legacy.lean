import AgTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain AgTax.country args
