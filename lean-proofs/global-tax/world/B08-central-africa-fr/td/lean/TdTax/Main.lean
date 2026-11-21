import TdTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain TdTax.country args
