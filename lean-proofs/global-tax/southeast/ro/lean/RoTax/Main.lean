import RoTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.countryMain RoTax.country args
