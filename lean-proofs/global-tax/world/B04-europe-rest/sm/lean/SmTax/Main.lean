import SmTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain SmTax.country args
