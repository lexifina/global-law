import GwTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain GwTax.country args
