import CuTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain CuTax.country args
