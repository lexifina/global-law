# United Kingdom, 2025-26

The UK model used in this comparison is the one in [`../../official-checks/uk-model`](../../official-checks/uk-model):
income tax, capital gains tax, Class 1, 2 and 4 National Insurance, Child Benefit and the high income child benefit
charge, Lean 4 core v4.35.0, exe `uktax`.
It is the same model, file for file, so it is not copied here; its `HOWWRITTEN.md`, `EXAMPLE.md` and `harness/` are
there too.

This folder adds the model's two reports:

- [`RESULTS.md`](RESULTS.md): the checks against HMRC's and GOV.UK's published figures, HMRC's payroll test data,
  PolicyEngine-UK and the OECD, and the proved properties.
- [`FINDINGS.md`](FINDINGS.md): every difference found and who is right, with the authority.

In both, `lean/`, `harness/`, `EXAMPLE.md` and `HOWWRITTEN.md` refer to the files in
[`../../official-checks/uk-model`](../../official-checks/uk-model); `runs/` and `refs/` were not published (see
[`../refs/README.md`](../refs/README.md)).
