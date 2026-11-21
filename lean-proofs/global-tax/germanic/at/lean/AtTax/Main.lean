import AtTax.Household

def main (args : List String) : IO UInt32 := TaxKernel.countryMain AtTax.country args
