import KpTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain KpTax.country args
