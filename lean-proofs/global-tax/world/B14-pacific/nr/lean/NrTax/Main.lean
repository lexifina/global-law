import NrTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain NrTax.country args
