import NaTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain NaTax.country args
