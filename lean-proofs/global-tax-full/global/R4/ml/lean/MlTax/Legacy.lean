import MlTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain MlTax.country args
