import TlTax.Basic

def legacyMain (args : List String) : IO UInt32 := TaxKernel.worldMain TlTax.country args
