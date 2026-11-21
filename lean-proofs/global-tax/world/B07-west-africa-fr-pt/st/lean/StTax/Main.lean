import StTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain StTax.country args
