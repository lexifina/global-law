import ClTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain ClTax.country args
