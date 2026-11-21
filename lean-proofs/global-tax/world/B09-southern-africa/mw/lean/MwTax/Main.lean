import MwTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain MwTax.country args
