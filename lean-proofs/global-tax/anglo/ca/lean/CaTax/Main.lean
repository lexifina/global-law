import CaTax.Household

def main (args : List String) : IO UInt32 := TaxKernel.countryMain CaTax.country args
