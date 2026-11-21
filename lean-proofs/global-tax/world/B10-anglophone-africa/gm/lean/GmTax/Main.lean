import GmTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain GmTax.country args
