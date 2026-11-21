import PkTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain PkTax.country args
