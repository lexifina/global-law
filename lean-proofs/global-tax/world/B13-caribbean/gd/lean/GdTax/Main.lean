import GdTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain GdTax.country args
