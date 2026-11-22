import JoTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain JoTax.country args
