import EeTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.countryMain EeTax.country args
