import MxTax.Household

/-! `mxtax`: canonical households (JSONL) in, contract outputs (JSONL) out (TaxKernel.countryMain). -/

def legacyMain (args : List String) : IO UInt32 := TaxKernel.countryMain MxTax.country args
