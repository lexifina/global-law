# Lindquist, "State Politics and the Judiciary"

Status: NOT OBTAINED — needs user decision on the data-use agreement

- DOI: https://doi.org/10.15139/S3/12150 -> https://dataverse.unc.edu/citation?persistentId=doi:10.15139/S3/12150 (Odum Institute / SPPQ Dataverse, UNC)
- Metadata API: https://dataverse.unc.edu/api/datasets/:persistentId/?persistentId=doi:10.15139/S3/12150 (saved as `meta.json`)
- Accessed: 2026-11-13
- Author: Lindquist, Stefanie. Distribution date 2007; published in Dataverse 2016-01-04; version 1.0.
- Keyword: Judicial politics

## Description (verbatim)

> We gather data on overruling decisions in the fifty state supreme courts over the period of their histories. This will produce a comprehensive database of all overruled and overruling cases decided by each state Supreme Court.

## Licence and terms

- `license`: none set (no CC0 or other licence)
- `termsOfAccess`, `restrictions`, `conditions`: none; `fileAccessRequest`: false; no guestbook seen in the metadata
- `termsOfUse` (verbatim):

> **Conditions**
> User agrees that he/she will use these data only for analysis purposes and not take any actions to identify or contact individuals, communities, or organizations. User agrees to use appropriate safeguards to protect the data from misuse and shall promptly notify the State Politics and  Policy Quarterly (SPPQ) of any unauthorized or impermissible use or disclosure of the data of which he/she becomes aware.
> **Disclaimer**
> Files are offered "as is" with no warranty or claim of fitness for any purpose. In no event shall the University or SPPQ be liable for any actual, incidental or consequential damages arising from use of these files.
> By clicking the "I agree" checkbox, below, I confirm that I have read and understood each and every term set forth in the terms and conditions for the use of data and other materials found above, and I agree to be bound by all of such terms and conditions. If I do not understand or agree to all of the terms and conditions, I must not use or download any data or other materials.

- `disclaimer` (verbatim):

> The *State Politics & Policy Quarterly* and the Odum Institute for Research in Social Science are not responsible for the accuracy or quality of data uploaded within the *SPPQ* Dataverse, for the use of those data, or for interpretations or conclusions based on their use.

## Files (all flagged `restricted: false`, but all sit under the terms above)

| file id | name | bytes |
|---|---|---|
| 7185187 | Annual State Level Data 1975-2006FULL.xls | 3,842,560 |
| 7185198 | codebook.doc | 43,008 |
| 7185190 | Codebook updated.doc | 43,008 |
| 7185194 | codes.pdf | 108,856 |
| 7185197 | crime.xls | 181,248 |
| 7185192 | .DS_Store | 6,148 |
| 7185189 | economicsandbusiness.xls | 254,464 |
| 7185186 | education.xls | 175,104 |
| 7185196 | index.html | 5,100 |
| 7185199 | politics.xls | 121,344 |
| 7185195 | population.xls | 229,888 |
| 7185193 | statedata.xls | 729,088 |
| 7185191 | state_politics_and_the_judiciary_codebook.pdf | 192,733 |
| 7185200 | state_politics_and_the_judiciary_v91.tab (orig .sav) | 2,419,956 |
| 7185201 | state_politics_and_the_judiciary_v9.tab (orig .dta) | 1,456,809 |
| 7185188 | update.doc | 30,208 |
| 7185185 | Updates.pdf | 40,962 |

## Finding

No file is reachable without the "I agree" step. The terms apply to "any data or other materials", codebooks included. The API would serve the unrestricted files directly, but that only skips the click-through, so nothing was downloaded and `raw/` was not created.

Whether the files contain case-level overruled/overruling pairs therefore can't be checked against the codebook. The description says the project's aim is "a comprehensive database of all overruled and overruling cases". However, the file list (annual state-level xls files on crime, economics, education, politics and population for 1975-2006, plus v9/v91 .tab) suggests the deposit may be a state-year panel rather than a list of case pairs. This is unconfirmed.
