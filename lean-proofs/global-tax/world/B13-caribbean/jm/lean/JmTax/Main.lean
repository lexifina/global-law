import JmTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain JmTax.country args
