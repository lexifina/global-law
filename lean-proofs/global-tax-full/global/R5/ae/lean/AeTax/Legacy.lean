import AeTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain AeTax.country args
