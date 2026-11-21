import AgTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain AgTax.country args
