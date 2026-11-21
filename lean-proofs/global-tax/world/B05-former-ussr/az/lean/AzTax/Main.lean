import AzTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain AzTax.country args
