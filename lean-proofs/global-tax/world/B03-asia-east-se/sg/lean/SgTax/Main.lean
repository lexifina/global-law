import SgTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain SgTax.country args
