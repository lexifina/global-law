import RuTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain RuTax.country args
