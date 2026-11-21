import BsTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain BsTax.country args
