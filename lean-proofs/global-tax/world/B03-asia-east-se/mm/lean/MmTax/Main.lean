import MmTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain MmTax.country args
