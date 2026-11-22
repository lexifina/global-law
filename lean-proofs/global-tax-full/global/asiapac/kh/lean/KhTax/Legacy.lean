import KhTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain KhTax.country args
