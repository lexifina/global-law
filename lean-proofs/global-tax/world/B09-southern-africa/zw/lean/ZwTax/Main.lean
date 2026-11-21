import ZwTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain ZwTax.country args
