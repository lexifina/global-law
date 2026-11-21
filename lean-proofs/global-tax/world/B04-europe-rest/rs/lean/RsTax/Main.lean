import RsTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain RsTax.country args
