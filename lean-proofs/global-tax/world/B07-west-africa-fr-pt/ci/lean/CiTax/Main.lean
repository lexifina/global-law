import CiTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain CiTax.country args
