import NiTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain NiTax.country args
