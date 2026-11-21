import MkTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain MkTax.country args
