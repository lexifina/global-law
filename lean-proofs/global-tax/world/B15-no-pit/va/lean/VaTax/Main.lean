import VaTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain VaTax.country args
