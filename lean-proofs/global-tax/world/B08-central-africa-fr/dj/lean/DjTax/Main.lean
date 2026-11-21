import DjTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain DjTax.country args
