import IlTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain IlTax.country args
