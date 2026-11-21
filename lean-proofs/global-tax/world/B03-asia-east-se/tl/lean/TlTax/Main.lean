import TlTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain TlTax.country args
