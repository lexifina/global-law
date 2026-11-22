import DeGlobal.Basic

/-! # Germany: the kernel-2.0 pilot (`cmp20/global/pilots/de`, copied unchanged into `Basic.lean`) is the base;
the Europe builder's families are appended to it (`withFamily_charges`: nothing the pilot computes changes). -/

namespace DeGlobal
open TaxKernel TaxKernel.Global

def base : GlobalModel := DeGlobal.model

end DeGlobal
