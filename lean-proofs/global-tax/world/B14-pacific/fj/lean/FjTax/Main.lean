import FjTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain FjTax.country args
