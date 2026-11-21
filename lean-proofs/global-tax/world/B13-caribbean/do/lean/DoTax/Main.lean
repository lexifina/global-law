import DoTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain DoTax.country args
