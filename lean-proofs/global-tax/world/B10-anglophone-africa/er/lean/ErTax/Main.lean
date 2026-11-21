import ErTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain ErTax.country args
