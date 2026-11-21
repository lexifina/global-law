import McTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain McTax.country args
