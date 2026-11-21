import LvTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.countryMain LvTax.country args
