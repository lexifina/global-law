import NgTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain NgTax.country args
