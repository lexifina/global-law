import RwTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain RwTax.country args
