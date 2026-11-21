import MdTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain MdTax.country args
