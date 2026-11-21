import SiTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.countryMain SiTax.country args
