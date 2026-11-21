import FmTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain FmTax.country args
