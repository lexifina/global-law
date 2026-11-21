import GhTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain GhTax.country args
