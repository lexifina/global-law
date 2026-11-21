import TgTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain TgTax.country args
