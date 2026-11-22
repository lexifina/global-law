# CN (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)
- **CN FTR-1 (1200 CIT, model fix).** Small low-profit enterprises were taxed at 25 % (20 % only with a flag). 财政部
  税务总局公告2023年第12号 三: "对小型微利企业减按25%计算应纳税所得额，按20%的税率缴纳企业所得税政策，延续执行至2027年12月31日";
  五: 年度应纳税所得额不超过300万元、从业人数不超过300人、资产总额不超过5000万元 (gov.cn 国务院部门文件, `cn/law/mof/`). Now 5 % on
  the entity's own figures; 6 `#guard`s. PIT unchanged.
- **CN FTS-1, tax-calculator-pro (34271041-droid), `cn_ft_cit_taxcalcpro_grid` (software error).** The tool taxes a
  small low-profit enterprise at the nominal 20 % of 企业所得税法 art. 28 on its whole profit, without 公告2023年第12号
  三 (25 % of the income at 20 %, in force to 2027-12-31): all 126 dev misses, model / referee = 0.25 exactly (the
  builder's note confirmed).
