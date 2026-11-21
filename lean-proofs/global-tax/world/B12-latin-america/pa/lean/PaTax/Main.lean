import PaTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain PaTax.country args
