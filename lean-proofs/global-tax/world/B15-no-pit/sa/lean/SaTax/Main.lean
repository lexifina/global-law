import SaTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain SaTax.country args
