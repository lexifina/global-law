import SsTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain SsTax.country args
