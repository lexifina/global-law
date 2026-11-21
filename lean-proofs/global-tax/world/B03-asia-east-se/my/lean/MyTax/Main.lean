import MyTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain MyTax.country args
