import MtTax.Model

def main (args : List String) : IO UInt32 := TaxKernel.countryMain MtTax.country args
