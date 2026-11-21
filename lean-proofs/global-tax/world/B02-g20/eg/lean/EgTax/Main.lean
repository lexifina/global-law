import EgTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain EgTax.country args
