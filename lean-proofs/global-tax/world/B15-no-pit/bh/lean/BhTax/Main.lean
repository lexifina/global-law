import BhTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain BhTax.country args
