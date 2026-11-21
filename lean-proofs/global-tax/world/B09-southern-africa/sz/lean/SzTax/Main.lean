import SzTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain SzTax.country args
