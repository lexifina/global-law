import MzTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain MzTax.country args
