import CfTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain CfTax.country args
