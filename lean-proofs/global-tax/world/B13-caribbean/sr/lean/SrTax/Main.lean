import SrTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain SrTax.country args
