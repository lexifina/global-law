import IdTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain IdTax.country args
