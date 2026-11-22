import TaxKernel.World

/-!
# Vanuatu 2025: no income tax; Vanuatu National Provident Fund (VNPF) contribution

Sources (read 2026-11-20; `vu/law/`):
* Vanuatu National Provident Fund Act, Cap. 189, Consolidated Edition 2026 (VNPF's copy, `vnpf_act_consol_2026.pdf`;
  amended last by Act 25 of 2025): s. 25(1) "a contribution to the Fund is to be paid at the rate of 12 percent of
  that remuneration of which half is to be paid by the employer and half by the employee"; s. 25(1A) (inserted by
  Act 25 of 2025, "To avoid doubt") the employee pays 6 percent; s. 25(2) "No contribution shall be payable in respect
  of an employee in any month in which the total amount of the remuneration paid to that employee by any one employer
  is less than VT 3,000"; s. 1 "employee": any person employed in Vanuatu under a contract of service (not in the
  Schedule's excluded descriptions, not exempted by order): expatriates included (VNPF employer page: unless
  approved to contribute to an overseas fund).
* No income tax: no act levying a tax on individuals' income was found (the Global law corpus holds only the
  Constitution; FINDINGS F1).

Wages are spread evenly over 12 months, so the monthly VT 3,000 test is an annual VT 36,000 floor (all-or-nothing).
-/

namespace VuTax
open TaxKernel

def vnpfFloor : Int := 3000 * 12
def vnpf : Contribution := { name := "vnpf", sched := Schedule.flat 600, floor := vnpfFloor }   -- s. 25(1), (1A), (2)

def out (c : Canon) : Out :=
  let s := sumInts (c.adults.map fun a => vnpf.amount a.wages)
  Out.make c "VU" "VUV" 0 (employeeSocial := s)
    (detail := [Out.d "vnpf" s,
      Out.dStr "note" "no income tax act; VNPF Act Cap. 189 s. 25: 6 % employee share, none in a month under VT 3,000"])

def country : Country :=
  { code := "VU", name := "Vanuatu (employee)", currency := "VUV", year := "2025", compute := out }

end VuTax
