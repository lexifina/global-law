import IeTax.Household

def main (args : List String) : IO UInt32 := TaxKernel.countryMain IeTax.country args
