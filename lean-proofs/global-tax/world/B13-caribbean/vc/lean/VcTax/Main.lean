import VcTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain VcTax.country args
