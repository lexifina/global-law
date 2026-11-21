import CfTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain CfTax.country args
