# Vulnerabilities

Places where the law, as published, does not do what its makers meant: a fine that points at a deleted rule, a power
that refers to a section that was never enacted, a duty defined by an article since repealed. The
idea follows [Legal Zero-Days: A Novel Risk Vector for Advanced AI Systems](https://arxiv.org/html/2508.10050v1). This is theoretical research: nothing here has been tested in court.

[index.html](index.html) walks through five drafting mistakes in full: the rule, what the official text says, why
the two do not fit, the consequence, who could use it, and the strongest objections, each rated. Open it in a browser.

| # | Country | Mistake |
|---|---|---|
| 1 | Germany | The fine for using a shooting range the authority has shut down points at AWaffV § 12, deleted in 2020; the ban moved to § 27a WaffG, which carries no fine |
| 2 | Germany | Tax offices must send data to a body defined in GwG § 50c, a section that was never enacted (AO § 31b(3a)) |
| 3 | Brazil | The notice duty for minors' overtime points at four repealed articles (CLT art. 413) |
| 4 | Switzerland | Pest-control costs can only be charged for evading duties under LwG art. 151, repealed in 2025 (art. 154(2)) |
| 5 | Netherlands | Higher criminal fine ceilings in force on 1 January 2022, published on 5 January (Stb. 2022, 7) |

The page also lists further confirmed mistakes (Germany's railway-register and harbour fines, Chile's gun law, Fiji's
VAT offences, Malta's medicines ordinance and others) and, separately, "empty periods": rules that ran out before their
renewal took effect (Switzerland's GMO moratorium, France's algorithmic video surveillance, Spain's ban on church
heritage sales). Those are timing failures rather than mistakes in the text.

## How they were found

The corpora were read at pinned commits, never written to. Detectors looked across all of them at once for:

- references to provisions of the same act that were deleted or survive only as "(repealed)" placeholders, above all
  inside fine and penalty lists;
- publisher notes that an amendment could not be carried out;
- dates of entry into force before publication;
- time-limited rules extended only after they had run out.

A language model then sorted the candidates into corpus artefacts, lawful cases and candidate defects, a second model
argued against each survivor, and the strongest were checked by hand against gazettes, consolidated texts and
parliamentary papers. Most raw candidates turned out to be corpus build errors, which were reported to each corpus.
