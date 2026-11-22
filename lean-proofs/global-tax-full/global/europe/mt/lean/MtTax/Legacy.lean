import MtTax.Model

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain MtTax.country args
