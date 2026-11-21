import CrTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain CrTax.country args
