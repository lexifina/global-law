import SdTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain SdTax.country args
