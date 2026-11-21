import HrTax.Household

def main (args : List String) : IO UInt32 := TaxKernel.countryMain HrTax.country args
