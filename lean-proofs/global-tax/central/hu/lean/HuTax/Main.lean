import HuTax.Household

def main (args : List String) : IO UInt32 := TaxKernel.countryMain HuTax.country args
