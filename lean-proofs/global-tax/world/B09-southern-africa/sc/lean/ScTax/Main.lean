import ScTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain ScTax.country args
