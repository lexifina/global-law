import KiTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain KiTax.country args
