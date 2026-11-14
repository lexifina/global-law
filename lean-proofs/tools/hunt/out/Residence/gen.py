import sys
src=open('LegalProofs/USTax/Hunt/Residence.lean',encoding='utf-8',newline='').read()
i=src.index("/-! Recorded runs")
head=src[:i]; tail="\nend Legal.USTax.Hunt.Residence\n"
sc={
 'J3_visa_us_whole_h6_endInUS': "search { base with grid := whole, horizon := 6, maxReloc := 4, endInUS := true } visaHolder",
 'N_newcomer_arrival_h2': "search { base with grid := arrival } newcomer",
 'N2_student_arrival_h2': "search { base with grid := arrival, student := true } student",
 'M_gc9_realty_covered_coarse_h2': "search { base with grid := coarse, asset := .usRealty } greenCard9",
 'M2_gc9_realty_notcovered_coarse_h2': "search { base with grid := coarse, asset := .usRealty, covered := false } greenCard9",
 'M3_gc9_us_notcovered_coarse_h2': "search { base with grid := coarse, covered := false } greenCard9",
 'D2_citizen_us_notcovered_coarse_h2': "search { base with grid := coarse, covered := false } citizen",
 'A_visa_us_fine_h2': "search base visaHolder",
 'B_visa_foreign_coarse_h3': "search { base with grid := coarse, asset := .foreignStock, horizon := 3 } visaHolder",
 'C_visa_us_coarse_h3': "search { base with grid := coarse, horizon := 3 } visaHolder",
 'D_citizen_us_coarse_h2': "search { base with grid := coarse } citizen",
 'E_gc9_us_coarse_h2': "search { base with grid := coarse } greenCard9",
 'E2_gc3_us_coarse_h2': "search { base with grid := coarse } greenCard3",
 'F_newcomer_us_fine_h2': "search base newcomer",
 'G_student_us_fine_h2': "search { base with student := true } student",
 'H_visa_realty_coarse_h2': "search { base with grid := coarse, asset := .usRealty } visaHolder",
 'I_citizen_gifts_coarse_h2': "search { base with grid := coarse, gifts := true } citizen",
 'I2_visa_gifts_coarse_h2': "search { base with grid := coarse, gifts := true } visaHolder",
 'I3_gc9_gifts_realty_coarse_h2': "search { base with grid := coarse, gifts := true, asset := .usRealty } greenCard9",
 'J_visa_us_whole_h6': "search { base with grid := whole, horizon := 6, maxReloc := 4 } visaHolder",
 'J2_visa_foreign_whole_h6': "search { base with grid := whole, horizon := 6, maxReloc := 4, asset := .foreignStock } visaHolder",
 'K_citizen_foreigntax_coarse_h2': "search { base with grid := coarse, f := 2500, fg := 1500 } citizen",
 'L_gc9_foreign_coarse_h3': "search { base with grid := coarse, asset := .foreignStock, horizon := 3 } greenCard9",
}
for k in sys.argv[1:]:
    open(f'tools/hunt/out/Residence/{k}.lean','w',encoding='utf-8',newline='').write(head+"#eval "+sc[k]+"\n"+tail)
