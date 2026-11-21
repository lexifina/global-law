import BbTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain BbTax.country args
