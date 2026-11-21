import UaTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain UaTax.country args
