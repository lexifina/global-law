import MhTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain MhTax.country args
