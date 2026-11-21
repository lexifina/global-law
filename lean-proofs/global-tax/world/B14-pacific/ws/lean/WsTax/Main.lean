import WsTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain WsTax.country args
