import LbTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain LbTax.country args
