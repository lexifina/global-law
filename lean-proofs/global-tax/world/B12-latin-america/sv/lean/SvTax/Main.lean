import SvTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain SvTax.country args
