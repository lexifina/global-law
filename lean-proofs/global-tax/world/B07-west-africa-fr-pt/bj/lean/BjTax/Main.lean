import BjTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain BjTax.country args
