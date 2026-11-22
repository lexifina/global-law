import TaxKernel.Global
import R5Common

/-!
# Georgia 2025: employer funded-pension contribution (2200)

Law on Funded Pensions No. 3303 (2018), art. 3(6)(ა), as in force on 2025-07-01 (1.x `law/pension_3_21_20250701.txt`,
fetched by the 1.x builder): the employer pays at its own expense "ხელფასის 2 პროცენტ[ს]" for each participating
employee. Participation follows the 1.x model's convention (every employee participates). No other employer social
contribution exists (Georgia abolished the social tax): heading 2200 holds only this.
-/

namespace GeGlobal
open TaxKernel TaxKernel.Global R5Common

def social : Family :=
  { name := "2200 საპენსიო შენატანი (დამსაქმებელი)", covers := [.sscEmployer],
    run := fun _ g _ => employerOn "საპენსიო შენატანი (დამსაქმებელი)" "Law on Funded Pensions art. 3(6)(ა) (2 %)" 200 (-1) g }

#guard (employerOn "x" "y" 200 (-1) { id := "t", household := { id := "t", adults := [{ wages := 50000 }] } }).map (·.due) == [1000]

end GeGlobal
