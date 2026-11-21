import CdTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain CdTax.country args
