import RwTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain RwTax.country args
