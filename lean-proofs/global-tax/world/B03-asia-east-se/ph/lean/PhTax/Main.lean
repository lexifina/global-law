import PhTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain PhTax.country args
