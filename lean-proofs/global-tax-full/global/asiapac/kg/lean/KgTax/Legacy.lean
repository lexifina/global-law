import KgTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain KgTax.country args
