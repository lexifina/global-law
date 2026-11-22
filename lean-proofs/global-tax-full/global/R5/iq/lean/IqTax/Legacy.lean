import IqTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain IqTax.country args
