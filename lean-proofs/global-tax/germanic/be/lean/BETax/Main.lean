import BETax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.countryMain BETax.country args
