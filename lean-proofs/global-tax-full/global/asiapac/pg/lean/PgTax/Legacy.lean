import PgTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain PgTax.country args
