import PhTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain PhTax.country args
