import IsTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.countryMain IsTax.country args
