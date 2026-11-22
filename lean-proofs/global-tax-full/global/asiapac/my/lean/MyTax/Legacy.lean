import MyTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain MyTax.country args
