import MlTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain MlTax.country args
