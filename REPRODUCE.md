# Git for Global Law: how this repository was made, and how to make it again

This file records exactly how the repository was built: what it was built from, the commands, the software, the
decisions made by hand, and what an AI model did and did not do. Anyone with Python and git, and read access to the
three corpus repositories, can rebuild it and check it hash for hash.

## Short version

```sh
git clone --recurse-submodules https://github.com/lexifina/global-law && cd global-law
python -m unittest discover -s tests -v                       # 48 checks, described below
python tools/build.py ../rebuilt --date 2026-10-28             # the same build, from the published corpus repos
git -C ../rebuilt log --format=%H                              # the same hashes as `git log --format=%H` here
```

On 28 October 2026 two builds into separate empty folders gave the same 403188 commit hashes, from the first commit
(the jurisdiction tree, dated 1 January 1970) to the last (this documentation). The build reads the corpus
repositories as they are published, so it rebuilds hash for hash for as long as those repositories are at the commits
listed below.

## What it is built from

This repository contains no legal text of its own. It is built from three repositories, each with its own
REPRODUCE.md recording how its text was obtained. At this build they were at these commits, which are the commits this
repository pins at its head:

| Path here | Repository | Commit |
| --- | --- | --- |
| `andorra/national/acts` | https://github.com/lexifina/andorra-law | `b4cf79ecfb8ae39af6f3eef00af7f0110dd8e5a3` |
| `albania/national/acts` | https://github.com/lexifina/albania-law | `20f957b4cc6944d4fcc51323cc267d1c7b90d67f` |
| `armenia/national/acts` | https://github.com/lexifina/armenia-law | `3f01702f5e6b6d78e4f47db55ddb863d8126c80f` |
| `angola/national/acts` | https://github.com/lexifina/angola-law | `1a73c1569157f6e09708df5b3ea2bab08c500a23` |
| `argentina/national/acts` | https://github.com/lexifina/argentina-law | `bc9bd216dacb9c84554b63de510a7eed3068537c` |
| `austria/bund/acts` | https://github.com/lexifina/austria-law | `4cc372aef9323b9fb5b0478ba4d925e8dcb21863` |
| `australia/australian-capital-territory/acts` | https://github.com/lexifina/australia-australian-capital-territory-law | `cb3db9f8e2039a5e3d76d2137f3f838755357c49` |
| `australia/federal/acts` | https://github.com/lexifina/australia-law | `003cdb4cb9c69014439b9115384d626de946eb49` |
| `australia/northern-territory/acts` | https://github.com/lexifina/australia-northern-territory-law | `e412d88af5aabad934cfda9aa45eaee2a8a51dd0` |
| `australia/south-australia/acts` | https://github.com/lexifina/australia-south-australia-law | `8ec14a6ce08f5c82fb61a0a550ddec0603bcc3a3` |
| `australia/tasmania/acts` | https://github.com/lexifina/australia-tasmania-law | `23a1c18f56decd1ee2b93f73025b9b7b4069c33c` |
| `australia/western-australia/acts` | https://github.com/lexifina/australia-western-australia-law | `0d18ea9b2afc597448b9723555a723ad3ef5f6b8` |
| `aland/national/acts` | https://github.com/lexifina/aland-law | `684156dfc5ce445ad2f1bc0adec9c5cf998c5c08` |
| `azerbaijan/national/acts` | https://github.com/lexifina/azerbaijan-law | `08f3d7e2f1eafd21e084bf73931d346903553599` |
| `bulgaria/national/acts` | https://github.com/lexifina/bulgaria-law | `476e565a2760b862c90fc1b9efd1772d666ef248` |
| `bolivia/national/acts` | https://github.com/lexifina/bolivia-law | `bd90e24991b39b706cc4ec008f4ce27784c0720c` |
| `brazil/national/acts` | https://github.com/lexifina/brazil-law | `09db458187d61fe69368717bce8363efe15d7d0d` |
| `bahamas/national/acts` | https://github.com/lexifina/bahamas-law | `b13688b3b421f479ae819f752900eedf08da2209` |
| `botswana/national/acts` | https://github.com/lexifina/botswana-law | `8e6f8772441eb074e7c33caffa409873bf48f6c2` |
| `belize/national/acts` | https://github.com/lexifina/belize-law | `61093f9e0be0186d66d62be8834ccc2af65784cc` |
| `canada/federal/acts` | https://github.com/lexifina/canada-law | `60a8dcfa31b90a40b314d922fca8104a0ecb2070` |
| `canada/newfoundland-and-labrador/acts` | https://github.com/lexifina/canada-newfoundland-and-labrador-law | `cf692c25d154d13cb12a6a8e346f7605d5728a34` |
| `canada/northwest-territories/acts` | https://github.com/lexifina/canada-northwest-territories-law | `8b943cfe6f460d2d109f546fe4ac93ca0355f102` |
| `dr-congo/national/acts` | https://github.com/lexifina/dr-congo-law | `cb1f4afcee5c1647cbf0eba273b26cc2180c4316` |
| `switzerland/bund/acts` | https://github.com/lexifina/switzerland-law | `06696ea19cf23d362f02ac688ff59df3fdb14aab` |
| `cote-divoire/national/acts` | https://github.com/lexifina/cote-divoire-law | `16ef33c9b6264afe1a55a5a806d1f1b1a0ce1b10` |
| `cook-islands/national/acts` | https://github.com/lexifina/cook-islands-law | `00d1944e525eb0e2fe56db0504184e0ab8fd7f2c` |
| `chile/national/acts` | https://github.com/lexifina/chile-law | `57ddcc78b77c60558e16ea5bd0565a828ad71774` |
| `china/national/acts` | https://github.com/lexifina/china-law | `334c5528af9b757e5d22e6740c0b7d2a1e86672a` |
| `colombia/national/acts` | https://github.com/lexifina/colombia-law | `6f6fbbda4f002ccbf4fc14d1aee145c76037cb33` |
| `costa-rica/national/acts` | https://github.com/lexifina/costa-rica-law | `2c8e931fc16543b18cceb06fadf46f596ef58d46` |
| `cyprus/national/acts` | https://github.com/lexifina/cyprus-law | `8e6847e4a151b2795d4d9b536c0622d736a52f33` |
| `czechia/national/acts` | https://github.com/lexifina/czechia-law | `35e53bb38ca677a77c3a0ea218b6db7dce7cf89d` |
| `germany/bund/acts` | https://github.com/lexifina/germany-law | `6f3913a35a8ed38c01d9f1919fa1e3af0ba01f9f` |
| `denmark/national/acts` | https://github.com/lexifina/denmark-law | `3100e0fe6d8dac096fbf8e08744177197b5d97b3` |
| `dominican-republic/national/acts` | https://github.com/lexifina/dominican-republic-law | `e3bf2d77e19b6f4af532ef07dfff8044382a64a1` |
| `ecuador/national/acts` | https://github.com/lexifina/ecuador-law | `d29cefecfb59530e840b484280bcc112f045c577` |
| `estonia/national/acts` | https://github.com/lexifina/estonia-law | `91c786e18330af4b6cb5b04323c7b92532f7f912` |
| `spain/national/acts` | https://github.com/lexifina/spain-law | `513d8526e652a8ca81e9239aab5154040d6f9ad8` |
| `finland/national/acts` | https://github.com/lexifina/finland-law | `56b5ab8bafd6007f1cafdcef57c8652851249414` |
| `fiji/national/acts` | https://github.com/lexifina/fiji-law | `3ce68fd71d38a5e3eb7f6301a7ae28f9bbd9222d` |
| `micronesia/national/acts` | https://github.com/lexifina/micronesia-law | `e47ba7a924d2b9b1ea993cfe909f9e3b7ef3efc1` |
| `faroe-islands/national/acts` | https://github.com/lexifina/faroe-islands-law | `8624cee7b535890a2a91407ae2df488c8471bbc0` |
| `france/national/acts` | https://github.com/lexifina/france-law | `a6e16b131b5821792b172eab692c860339397a51` |
| `united-kingdom/uk/legislation` | https://github.com/lexifina/united-kingdom-law | `2d4137c6246be7396dc1fc930b71ccd6aa9f75a7` |
| `georgia/national/acts` | https://github.com/lexifina/georgia-law | `ef77971d51e67faddd63178df242f546890d9ce5` |
| `ghana/national/acts` | https://github.com/lexifina/ghana-law | `28341b4407ac073ea730d1232ae77c297c63dfd6` |
| `gibraltar/national/acts` | https://github.com/lexifina/gibraltar-law | `ecddb5d0851f29c189eadb18c6cccba9965b97b9` |
| `greenland/national/acts` | https://github.com/lexifina/greenland-law | `e132142bb86dc9346234fe7ca7d6c96507b6c644` |
| `guinea/national/acts` | https://github.com/lexifina/guinea-law | `1528198d92d503a26d328d484e4df512e993eaef` |
| `greece/national/acts` | https://github.com/lexifina/greece-law | `ccf04e0190b175e1ea575654d2c3e7de61754a28` |
| `guyana/national/acts` | https://github.com/lexifina/guyana-law | `f5149ae7b7fcebba40ab001c7ea5036198125ded` |
| `hong-kong/national/acts` | https://github.com/lexifina/hong-kong-law | `c09c3ad5a097b1a9387d3a260f27a0d87021cd24` |
| `croatia/national/acts` | https://github.com/lexifina/croatia-law | `309ababd219a2b68480b24561579aa6c9b4adc9c` |
| `ireland/national/acts` | https://github.com/lexifina/ireland-law | `5bf2da7b57ed845140bf8e71e8d67a51c4d2292d` |
| `italy/national/acts` | https://github.com/lexifina/italy-law | `38f884dd1eb91c95cfafb419528d77da30b8fb87` |
| `japan/national/acts` | https://github.com/lexifina/japan-law | `9df83c895787f1b398320041c8436c03aee86342` |
| `kenya/national/acts` | https://github.com/lexifina/kenya-law | `f9a6d26f99d017720cc2a69c704de0abfabf9440` |
| `kyrgyzstan/national/acts` | https://github.com/lexifina/kyrgyzstan-law | `74da05a27ee87e06ed440285c008b240e0ba342f` |
| `liechtenstein/national/acts` | https://github.com/lexifina/liechtenstein-law | `9643f48ffeb106e8a5ae104e776b814a550d1ce1` |
| `liberia/national/acts` | https://github.com/lexifina/liberia-law | `18744e71d894313d039e30214aaf886ca950e05a` |
| `lesotho/national/acts` | https://github.com/lexifina/lesotho-law | `2da8f55d9e0aa3020d111f89337b7e7fa14fcdc5` |
| `lithuania/national/acts` | https://github.com/lexifina/lithuania-law | `b5bfe7a1e621e483d899437df87b43619a09cd7d` |
| `luxembourg/national/acts` | https://github.com/lexifina/luxembourg-law | `16ebb76ea19ffd8b47b9313e585fe56c132f3bdc` |
| `monaco/national/acts` | https://github.com/lexifina/monaco-law | `04f2f086a9bdd71710fe7a0938e24cdb906dda95` |
| `moldova/national/acts` | https://github.com/lexifina/moldova-law | `383eb470e35fd45cd6ee593c56f5e8b902a547c8` |
| `montenegro/national/acts` | https://github.com/lexifina/montenegro-law | `cf16b160e81453d81588314e5d2fae83d38dac0d` |
| `madagascar/national/acts` | https://github.com/lexifina/madagascar-law | `e00ef50487a3ea426d093384b1f0f2cf26aaa290` |
| `north-macedonia/national/acts` | https://github.com/lexifina/north-macedonia-law | `7a6625e9d6398c8071fab8f0b16d56ed63154325` |
| `mali/national/acts` | https://github.com/lexifina/mali-law | `64d3d6203b4fbde3b908a302687d5d34c34fa04a` |
| `mongolia/national/acts` | https://github.com/lexifina/mongolia-law | `c98d57460c70e29bece8e24efcb3bffb78a4ceb7` |
| `malta/national/acts` | https://github.com/lexifina/malta-law | `7d25128590327a1ec6845f2ecd179b223bcf6a8f` |
| `malawi/national/acts` | https://github.com/lexifina/malawi-law | `2a966219d3150d1ecdaf9f047455a642c6b3eb0f` |
| `mexico/national/acts` | https://github.com/lexifina/mexico-law | `3c5843550b6b95e72d8e890dbeaed3739f422b6d` |
| `malaysia/national/acts` | https://github.com/lexifina/malaysia-law | `3eebb2a462e07b8ae9687bc670991a805f19c77e` |
| `namibia/national/acts` | https://github.com/lexifina/namibia-law | `054b4743b3688004781b94c8f852524f908d61f3` |
| `nigeria/national/acts` | https://github.com/lexifina/nigeria-law | `3176a08ec3072c385e7a3ba239df52415625dc2c` |
| `nicaragua/national/acts` | https://github.com/lexifina/nicaragua-law | `ec69becd3a541d4f099e37216787faaa8b77226a` |
| `netherlands/national/acts` | https://github.com/lexifina/netherlands-law | `fdb8e5f31cf5c5542583b4eb45da3fc8dfe59f17` |
| `norway/national/acts` | https://github.com/lexifina/norway-law | `48705e7b50710fbbc0783ec95bf2be811cdc1014` |
| `nauru/national/acts` | https://github.com/lexifina/nauru-law | `f16e226558b06993a7dacef14714a0a375113def` |
| `new-zealand/national/acts` | https://github.com/lexifina/new-zealand-law | `f505ca6cae1468ce1d95f54e19340cd011d79630` |
| `peru/national/acts` | https://github.com/lexifina/peru-law | `515df2b8750b44eb1a80d8b385134f751008cfc1` |
| `pakistan/national/acts` | https://github.com/lexifina/pakistan-law | `f550507fb46f419b2c6dccda1eb4c561e6db0b5e` |
| `poland/national/acts` | https://github.com/lexifina/poland-law | `7c0f3010a5a9daa6b307d9b10e05cc9b58901145` |
| `portugal/national/acts` | https://github.com/lexifina/portugal-law | `88c02e7aefc1ebeeb89911621a546734ae1240bc` |
| `palau/national/acts` | https://github.com/lexifina/palau-law | `dfe9d8de52cfb653190c31a8096fd970cef24ef2` |
| `paraguay/national/acts` | https://github.com/lexifina/paraguay-law | `90d7d58c4b0a5c5e3b545ef8918e7c94754128ca` |
| `romania/national/acts` | https://github.com/lexifina/romania-law | `ec269e743705364291b7fb6eba86a3d974ef11a0` |
| `russia/national/acts` | https://github.com/lexifina/russia-law | `eaaebe1b927444cd3439c7397d614309cbc2df30` |
| `rwanda/national/acts` | https://github.com/lexifina/rwanda-law | `121603ed4b20bcbdc22a8a93f0be713d86725b51` |
| `saudi-arabia/national/acts` | https://github.com/lexifina/saudi-arabia-law | `65f6fcf944ba04a7470912eeeaca496af3d82f41` |
| `seychelles/national/acts` | https://github.com/lexifina/seychelles-law | `eaf8ae00362f313df431e472dc852b3a45f986df` |
| `sweden/national/acts` | https://github.com/lexifina/sweden-law | `4073fa45f0bce755acab0507fca7247418920081` |
| `slovenia/national/acts` | https://github.com/lexifina/slovenia-law | `9387d5b524938a84486b20d616799e4134f2727f` |
| `slovakia/national/acts` | https://github.com/lexifina/slovakia-law | `a595c0404742d62ddadf2efe589646b5eaa0b09f` |
| `sierra-leone/national/acts` | https://github.com/lexifina/sierra-leone-law | `43292116fe4ab95dcda6ee0bbe3b8755cd7615a8` |
| `san-marino/national/acts` | https://github.com/lexifina/san-marino-law | `ea68a3a5c321ef86ddfc85b809e7f315b7b3a908` |
| `senegal/national/acts` | https://github.com/lexifina/senegal-law | `813c104879cd6d1b4c4a336733d5a40ce288fb43` |
| `suriname/national/acts` | https://github.com/lexifina/suriname-law | `f8bf52f5a8b1fcf96f69ef5be5294c17805a4b37` |
| `eswatini/national/acts` | https://github.com/lexifina/eswatini-law | `d0652e05b270a0070323a4c9c514d2432972980b` |
| `togo/national/acts` | https://github.com/lexifina/togo-law | `10b1d016ebd4e8fd69daa3414a9f100a2ed8efed` |
| `thailand/national/acts` | https://github.com/lexifina/thailand-law | `3f8fce0c6635742b347d4879f1acaa57b7ec8e0b` |
| `timor-leste/national/acts` | https://github.com/lexifina/timor-leste-law | `46095bfa4b4bad5d114b81cf94b8345629dd9785` |
| `turkey/national/acts` | https://github.com/lexifina/turkey-law | `7bd09670654aa06019eb03d4cae668be80b62705` |
| `trinidad-and-tobago/national/acts` | https://github.com/lexifina/trinidad-and-tobago-law | `7cbebc81fae61095e7d43b70a5d5067d90cfda38` |
| `taiwan/national/acts` | https://github.com/lexifina/taiwan-law | `1ed84a25e45679acade7d716361cc328d2a572c1` |
| `tanzania/national/acts` | https://github.com/lexifina/tanzania-law | `165e15932def1eac105570861a020e41c3e23c90` |
| `uganda/national/acts` | https://github.com/lexifina/uganda-law | `464b01f39153f6a55b05f36455fec4f60cc984e6` |
| `united-states/california/statutes` | https://github.com/lexifina/united-states-california-law | `a7096690ee942d855625bdf5076b870cc684615f` |
| `united-states/district-of-columbia/statutes` | https://github.com/lexifina/united-states-district-of-columbia-law | `dd1fc3d82cd99755f0bedb4ceab9783cb4682fb3` |
| `united-states/federal/usc` | https://github.com/lexifina/united-states-law | `f5537151bfb3ee25c86e87c70f945fbcf6ffd611` |
| `united-states/guam/acts` | https://github.com/lexifina/united-states-guam-law | `e3b8fb16af95cd98b2244c080e4ce3d6403a908b` |
| `united-states/indiana/statutes` | https://github.com/lexifina/united-states-indiana-law | `be5bfc582f1b21511920327d4510343137e246d6` |
| `united-states/new-jersey/statutes` | https://github.com/lexifina/united-states-new-jersey-law | `ae730bf98d9fe4b4cbe81cc17d425e48e6f1a83e` |
| `united-states/northern-mariana-islands/acts` | https://github.com/lexifina/united-states-northern-mariana-islands-law | `d23c95c9f4ceddba20f8043df14f340f9873b042` |
| `united-states/utah/statutes` | https://github.com/lexifina/united-states-utah-law | `000b9edcd1e44a6b69b6ae7b7132234e145e133c` |
| `uruguay/national/acts` | https://github.com/lexifina/uruguay-law | `37b6df4990347f183ac006dc389d6207350b710f` |
| `vatican-city/national/acts` | https://github.com/lexifina/vatican-city-law | `b07b82ef75b99b6a3b953e2dfcf8cfb53b5766d7` |
| `venezuela/national/acts` | https://github.com/lexifina/venezuela-law | `53ea22646e6f2a52a9157974732c593e42750b60` |
| `kosovo/national/acts` | https://github.com/lexifina/kosovo-law | `8485d729dcadcabf408767ea09eae9422272fd30` |
| `south-africa/national/acts` | https://github.com/lexifina/south-africa-law | `32ea831ba6e03b8cb06c47fdc5a8c8d5117d18f4` |
| `zambia/national/acts` | https://github.com/lexifina/zambia-law | `5ad4a6ec9d3881cdfb98da3fefd53a82fb0b8721` |
| `zimbabwe/national/acts` | https://github.com/lexifina/zimbabwe-law | `e7a3c9bfe4b0e44b1366f2f6c3278cb67fe2a3f6` |

The build reads each repository's commits on the first-parent line of its default branch, with their authors, dates
and message trailers, and its tags. It reads no file contents and makes no other network requests.

## The build, step by step

The build script is `tools/build.py`. It is the same file as `scripts/global-law/build.py` in Lexifina's own
repository (git blob `d1b094cb56666f87012d2e7ddf3a6d746042c176`). The reading tool `tools/law.py` has blob
`a4eed065182fff59d22f60f5f5a595435047eb19`, and the tests `tests/test_law.py` have blob
`b8f530cdac1abe5b1631b88d42f01c4de1dd0bcc`.

1. `python scripts/global-law/build.py <out> --date 2026-10-28 --site-data saas-webpage/app/watch/global-law/_data/global.json`
   - makes a bare clone of each corpus repository into `<out>/.git/corpus-cache/`
   - writes the first commit (the jurisdiction tree, `manifest.json` and `.gitmodules`)
   - writes one commit for each corpus commit, in in-force order, each moving that corpus's pin
   - copies each corpus's tags under its path
   - writes the last commit with the README, this file, the tools and the tests
   - and, with `--site-data`, writes the timeline that the page at lexifina.com/watch/global-law reads
2. The same command into a second empty folder. `git log --format=%H` was identical in both: 403188 commits.
3. `git submodule update --init`, then `python -m unittest discover -s tests -v`. All 48 tests passed.
4. `git push --force -u origin main` and `git push --force origin --tags` published it to GitHub. It is a private
   repository.
5. A fresh `git clone --recurse-submodules` from GitHub, then the tests again. All passed.

The build and the tools use only the Python standard library and git. They were run with Python 3.12.10 and git
2.46.0 on Windows 11. No AI model or other service is involved in building or reading the history.

## How the history is derived

Everything below is done by `tools/build.py`, deterministically. The same corpus commits give the same hashes.

- **Paths.** Each corpus sits at country (ISO 3166-1), then level, then corpus:
  - `germany/bund/acts`
  - `united-kingdom/uk/legislation`
  - `united-states/federal/usc`

  A sub-national level would use its ISO 3166-2 code, for example `us/ca`. Each folder above a corpus holds a
  `jurisdiction.json` naming it and listing its children.
- **Order.** The corpora's commits are merged by their in-force date, keeping each corpus's own order. Each
  corpus records its in-force date in a trailer:
  - `In-force:` for the US and UK corpora
  - `In-Kraft:` for the Grundgesetz

  A corpus commit without one (a starting edition, or documentation) is placed by its author date.
- **Commits.** There is one commit here for each corpus commit.
  - The author name, address and date are the corpus commit's. For the Grundgesetz before 1970 that date is the
    clamped 1970 date, because git cannot store earlier dates.
  - The committer is `Lexifina <global-law@lexifina.com>`, with the same date.
  - Where a date would fall before its parent's, it is raised to the parent's date, so the commit dates never go
    backwards.
  - The trailers are `Corpus`, `Corpus-commit`, `Law`, `In-force` and `Kind` (law, baseline or documentation). The
    tools rely on `In-force`, never on the commit date.
- **Tags.** Each corpus tag is copied as `<path>/<tag>`, for example `germany/bund/acts/gg/36`, pointing at
  the commit here that moved the corpus to the tagged commit.

## Decisions made by hand

1. **Folders above the corpora, not repositories.** Nested repositories would make every change ripple up through
   each level's pin. Folders give the same tree with one level of submodules.
2. **One commit here per corpus commit,** rather than one per day. That way each commit is one law taking effect,
   and its author is that law.
3. **The build reads the published repositories by default.** An earlier build read a local checkout and pinned a
   commit that had not been pushed, so a fresh clone could not fetch it. Building from local checkouts
   (`--local`) is kept for trying a corpus change before it is pushed. Such a build is not published.
4. **What is not in git.** Two things the Lexifina readers show are computed data rather than history:
   - which other provisions use a defined term or cite a section
   - notifications for a followed section

   Neither is in this repository. A later law's retroactive reach is in the corpus commit messages only, and does not
   change the text shown on earlier dates.

## What an AI model did

This repository was built on 28 October 2026 in **Claude Code**, Anthropic's coding tool, by the model **Claude Opus
5.5** (model id `claude-opus-5-5`). The model was working from a goal set by the user at Lexifina: to design a git
repository of "global law", with jurisdictions inside it and the law of each inside those, built from Lexifina's
existing corpus repositories, then to test it and publish a page about it.

The model:

- **Chose the design** described above and in the README, after reading the three corpus repositories' commits,
  trailers and tags.
- **Wrote all the code and text in this repository:** `tools/build.py`, `tools/law.py`, `tests/test_law.py`, the
  README and this file.
- **Ran the commands listed above** and checked the results: the tests, two builds compared hash for hash, and a
  fresh clone from GitHub.

The model did **not**:

- **Write or change any legal text.** This repository holds none. The text is in the corpus repositories, where it
  was copied by their own scripts from the official publishers, as their REPRODUCE.md files record.
- **Take part in building or reading the history.** No AI model is called by the build, the tools or the tests.

The user decided the scope, the owner (the Lexifina organisation) and that the repository is private. The work was not
reviewed line by line by a lawyer. For anything that matters, the legislation itself should be read.

## The tests

`tests/test_law.py` has 48 tests:

- **The tree.** Every level describes itself and its children, and the head pins each corpus at its latest commit.
- **The timeline.**
  - It is in in-force order, with one commit here per corpus commit.
  - Each commit moves exactly one pin.
  - Commit dates never go backwards.
- **Readings on a date.**
  - The US small business debtor limit is $7.5 million in 2021, gone in May 2022, back in July 2022 and gone in
    July 2024.
  - Grundgesetz Art. 12a appears from 28 June 1968, and Art. 91e from 27 July 2010.
  - Nothing is in force before 24 May 1949.
  - Every corpus matches being read on its own at six dates.
- **Against each corpus's own tools.**
  - Grundgesetz: six articles at seven dates from 1949 to 2017 agree with the corpus's `tools/stand_am.py`.
  - UK: every version in the corpus's `data/history.json`, rendered by the corpus's own builder, equals the file
    read here on that version's date.
- **The reader's questions.**
  - `log`: every law that changed a file, in order, with its in-force, enacted or made, and published dates.
  - Dates that differ: the SEND Regulations were made on 4 June and came into force on 1 September 2014.
  - `blame` names the law in each jurisdiction, and `words` credits each word: the restored §1182(1) to Pub. L.
    117-151, Art. 79 to both 1949 and 1954, one word of reg. 13(3) to the 2020 coronavirus regulations.
  - Copied tags point at the matching state.
  - A plain `git ls-tree` and `git show` gives the same text as the tools.
  - A date window lists laws from two countries in order.

## Changes to this repository after it was published

- **28 October 2026.** The repository moved from a personal account to the Lexifina organisation, and the corpus
  repositories followed. It was rebuilt with the new addresses and force-pushed, and later with this file and the
  build script added.
