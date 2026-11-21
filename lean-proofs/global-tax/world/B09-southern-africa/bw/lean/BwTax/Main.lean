import BwTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain BwTax.country args
