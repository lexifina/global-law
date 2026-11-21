import MgTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain MgTax.country args
