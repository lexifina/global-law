import DzTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain DzTax.country args
