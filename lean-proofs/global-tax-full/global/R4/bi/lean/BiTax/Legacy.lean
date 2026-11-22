import BiTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain BiTax.country args
