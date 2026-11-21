import CnTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain CnTax.country args
