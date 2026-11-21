import BdTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain BdTax.country args
