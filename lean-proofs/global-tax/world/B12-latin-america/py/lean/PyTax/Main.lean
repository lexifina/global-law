import PyTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain PyTax.country args
