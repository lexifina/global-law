import VeTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain VeTax.country args
