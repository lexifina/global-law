import DmTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain DmTax.country args
