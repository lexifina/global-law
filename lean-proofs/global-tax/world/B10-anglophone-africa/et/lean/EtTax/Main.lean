import EtTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain EtTax.country args
