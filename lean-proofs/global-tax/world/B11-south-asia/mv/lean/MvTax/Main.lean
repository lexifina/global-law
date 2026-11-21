import MvTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain MvTax.country args
