import BaTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain BaTax.country args
