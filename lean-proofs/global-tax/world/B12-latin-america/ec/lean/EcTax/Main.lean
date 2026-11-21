import EcTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain EcTax.country args
