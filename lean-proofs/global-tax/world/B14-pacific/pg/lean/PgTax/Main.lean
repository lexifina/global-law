import PgTax.Basic

def main (args : List String) : IO UInt32 := TaxKernel.worldMain PgTax.country args
