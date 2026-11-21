import SbTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain SbTax.country args
