import KzTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain KzTax.country args
