import KmTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain KmTax.country args
