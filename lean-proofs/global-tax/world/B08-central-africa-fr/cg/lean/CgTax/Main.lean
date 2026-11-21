import CgTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain CgTax.country args
