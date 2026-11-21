import NzTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.countryMain NzTax.country args
