import PsTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain PsTax.country args
