import NrTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain NrTax.country args
