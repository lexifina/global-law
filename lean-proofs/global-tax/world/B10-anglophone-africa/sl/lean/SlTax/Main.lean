import SlTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain SlTax.country args
