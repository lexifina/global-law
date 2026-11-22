import ToTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain ToTax.country args
