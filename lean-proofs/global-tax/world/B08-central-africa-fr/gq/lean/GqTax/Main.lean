import GqTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain GqTax.country args
