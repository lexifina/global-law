# Disagreements read (round6 `final2`, as of 20261112)

30 disagreements drawn at random (seed 20261113, `work/read_nodes.txt`) after scoring, from three strata:
16 of the 1,261 NEG misses whose Supreme Court order is in the corpus, 4 of the 567 NEG misses whose order is not,
and 10 of the 60 nodes the model shows `NEG_HIST` that the source does not code `NEG` (CLEAN or PART).
Reading packets (`dump_cases.py` → `work/read/<node>.txt`): key rows with the dataset's order texts, the corpus order
text, the model's status and history rows, and the lower decision's text. Read by three Claude sub-agents with one
brief each (no rule was changed afterwards).

## Result

| category | NEG misses, order in corpus (16) | NEG misses, order not in corpus (4) | model NEG on CLEAN/PART (10) | total |
|---|---|---|---|---|
| model missing | 16 | 4 | 0 | 20 |
| model wrong | 0 | 0 | 6 | 6 |
| mapping artefact | 0 | 0 | 4 | 4 |
| source wrong | 0 | 0 | 0 | 0 |
| link error | 0 | 0 | 0 | 0 |

No source error and no link error in 30 (every lower docket number, caption and docket-page date matched the linked
decision). `source_errors.tsv` is therefore empty (header only).

## NEG misses: why the model has nothing (20 of 20 "model missing")

Order not in the corpus (4: 385439, 1031399, 384315, 982024): the model cannot see the event; the corpus has very
few Supreme Court orders for 2006–2009 and after 2020 (recall on nodes whose order is not in the corpus: 5/572).

Order in the corpus (16): no admitted history row targets the lower decision in any of them. Visible causes:

- **Combined orders listing many captions** (Booker 2005, Dorsey 2012 GVR lists; 8 of 16: 821755, 1108716, 976423,
  553237, 1108035, 979546, 977647, 1004406): the order text carries e.g. "Reported below: 95 Fed. Appx. 376" for
  the case, but the model's memo linker did not attach it. The order cites the unpublished reporter as
  "Fed. Appx." while the corpus files the decision as "F. App'x"; and the caption/citation pairing inside a list of
  dozens of cases is positional. Orders dated 2005 (the Booker GVR year): recall 53/608 NEG nodes.
- **Head-matter-only orders with no citation below** (5: 1317661, 460979, 1210895, 1123633, 1196063): "C. A. 7th Cir.
  Certiorari granted, judgment vacated, and case remanded…" with no "Reported below"; only a docket number links
  them, which the model does not use (ROUND6.md lists post-2013 head-matter-only orders as cut for time).
- **Per curiam summary reversal citing the decision only in its citation list** (2: 1009196, 1107641); one with the
  caption reversed (Holland v. Jackson / Jackson v. Holland).
- **Corrupted citation in the order** (1: 1210559, "Reported below: 639 P. 3d 315" for 639 F.3d 315).
- 1196063: the model has only a `reinstated` row (7th Cir. on remand reinstated part of its opinion), no vacatur row.

## Model NEG on CLEAN/PART (10)

Model wrong (6), quoted from the reviewing text the model used:

- 1003131 — by 1011962, a 2014 5th Cir. panel in another appeal, withdrawing its own opinion: "The per curiam
  opinion dated April 2, 2014 is withdrawn and the following per curiam is substituted in its place."
- 6512785 — by 6515889, a different Texas case withdrawing its own opinion: "we withdraw our opinion and judgment of
  August 31, 2010".
- 1583596 — by 6323956, a Supreme Court stay denial: "The order heretofore entered by the Chief Justice is
  vacated." (an administrative stay, not the D.C. Circuit decision).
- 912444 — by 6305804, which vacated a later remedial order of the district court, not this merits decision
  ("we vacate the District Court's reme[dial order]").
- 6507115 — by 6400840 (Texas Supreme Court habeas): "Accordingly, we vacate the commitment order" — the trial
  court's order, not this court of appeals decision.
- 2874572 — by 2837068 (Indiana Supreme Court): "the order granting transfer is VACATED and transfer is DENIED. The
  Court of Appeals opinion … is no longer vacated … and is reinstated" — a reinstatement read as a vacatur.

Mapping artefact (4): the negative event is real and the source is right about its own petition.

- 5539404 — Oregon v. Guzek: the State's petition (04-928, a merits case, so not scored) vacated this Oregon Supreme
  Court judgment; the defendant's own petition (04-7698) was denied → node pooled CLEAN.
- 1408316 (Visciotti) and 566230 (Dewar) — cross-petitions: one side's petition summarily reversed / GVR'd, the
  other's denied → pooled PART; the model's NEG_HIST counts as agreement for PART but as a precision miss under the
  strict precision rule.
- 3621448 — Michigan Supreme Court reversed this decision on some claims only; the cert petition came from the other
  part (uncertain; the model's scope `all` is overbroad).

## Estimates (not tuned on)

On the NEG side every read miss was a real model miss; the measured recall is not depressed by link or source
errors in this sample (0/20 link or source errors; upper 95% bound 16%). Of the 60 model-NEG nodes outside `NEG`,
the read sample suggests about 60% are model errors and 40% real events the mapping does not credit (6/10, 4/10).
