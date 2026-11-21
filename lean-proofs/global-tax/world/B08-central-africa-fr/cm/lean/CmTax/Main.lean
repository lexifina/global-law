import CmTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain CmTax.country args
