import BrTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain BrTax.country args
