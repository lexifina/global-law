# Round 13 freeze

Frozen 2026-11-14 12:04. Variant `v13a` (data `round13/stage/v13a`, Lean output `round13/out/v13a`). Base v12a + Shadow rules D (16), S (11), A (8) [audited] + T4 (245), SCDB R2 v3 (76), EB12 v6 (101) [installed on user decision (below bar)]; reference differential 0 disagreements in every table.

The sealed halves (fresh lists and Shepardized, both burned), the h1 halves of the four round-8 keys (sixth use), songer_treat and brace_hall_state (fifth use), fedcir_dataset (fourth use), bhk_enbanc (third use) and fjc_idb_unpub (second use) are scored once on exactly these files (`round13/score_sealed13.sh v13a`); `freeze13.py --check` refuses if any line below no longer matches. Nothing is re-tuned after the sealed runs.

## Classes in the frozen build (on top of round 12's frozen v12a)

| class | source | rows | audit | basis |
|---|---|---|---|---|
| Shadow D: same person, second docket (filing window, one docket) | round13/agents/shadow13/cert_D | 16 | r13k01 whole class 14/15 = 0.933 [0.702, 0.988] (+1 read right in r11k01) | audited, at or above the 0.90 bar |
| Shadow S: officer successor (same office, other holder) | round13/agents/shadow13/cert_S | 11 | r13k02 whole class 9/9 = 1.000 [0.701, 1.000] (+2 read right in r11k01) | audited, at or above the 0.90 bar |
| Shadow A: agency acronym spelled out | round13/agents/shadow13/cert_A | 8 | r13k03 whole class 8/8 = 1.000 [0.676, 1.000] | audited, at or above the 0.90 bar |
| State T4: section-6 trial bridge (trialBridge claim + history_tbridge) | round10/agents/stlink10/delta_T4 | 245 | r10t04 right 68/80 = 0.850 [0.756, 0.912]; link+effect 74/80 = 0.925 | **installed on user decision (below bar)**: link+effect basis |
| SCDB R2 v3: en banc vacatur / rehearing en banc notes | round11/agents/scdb11/cert_r2v3 minus round13/lead/drop_r2v3_overlap.txt | 88 - 12 = 76 | r11b04 44/49 = 0.898 [0.782, 0.956] (fresh sample under 80) | **installed on user decision (below bar)** |
| En banc EB12 v6: E's own words vacate the panel opinion | round12/agents/enbanc12/cert_eb12b | 101 | r12e02 fresh remainder 26/27 = 0.963; r12e01 biased 64/67 | **installed on user decision (below bar)**: fresh sample under 80 (D12-4) |

R2 v3 x EB12 v6 (D13-2): the 12 identical (acting decision, target) pairs keep the EB12 v6 row only (7 same kind, 5
`rehearingEnBancGranted` vs `vacated`: the acting court's own vacatur words win; one row per pair).
Not installed: rule N (name form, item 4; dev 9/13 on non-key truths, not audited). Pending user decisions left as
they are: the 139 section-5.2 identity lines, the 47 OT2025 orders of Jan-Jun 2026 (still in the build, as in v12a),
data hygiene, New Jersey attribution.

```
wsl:~/caselaw2/r13_bin/caselaw2_r11v11d  binary sha1 a1cc4296022b1bd07401cc64b04e50449d0de9b3
ce8654e67f324864b11bf2d7625e26ced1ddbe58  round13/stage/v13a/treatments.tsv
3570179eed68b9fad4a6755bbb63f83b9cf01532  round13/stage/v13a/treatment_witness.tsv
9fa4c19eb768086d470171032e04d9ba040ec06c  round13/stage/v13a/treatment_class.tsv
19620d07895278d9ca834f1f48bf9e4bd7c5f488  round13/stage/v13a/history.tsv
6344a44fb2bcd9a2a2cb881165eef7450356f79c  round13/stage/v13a/history_anchor.tsv
1bc04d318f1d9ba040d63e78e4580498cf5d9a33  round13/stage/v13a/history_claim.tsv
eb8a18d6c8889f7b8b10e1c31c075bb6f7a9fc3b  round13/stage/v13a/joined.tsv
40a0ba7ef15d8f8a5f80b50c31b7687154633465  round13/stage/v13a/cert_text.tsv
aca63a3efe85a033be9f45d2468755054e1408cb  round13/stage/v13a/window_sha.tsv
1173dfb30aa4dc0f74cf71dc002c0880246a4009  round13/stage/v13a/cite_index.tsv
8bfc2cbcfa7e87d4c0b2cd80efe4b68148545f13  round13/stage/v13a/history_bridge.tsv
b4ba53d7c6a6126147a3d88e80ca0a20a747fe25  round13/stage/v13a/part_zone.tsv
7d959452b3428dfb6c5a26971e573e238de7fd54  round13/stage/v13a/history_remand.tsv
4e87a509c6fb27542b46008ae6baf6541bd56d5a  round13/stage/v13a/history_tbridge.tsv
88e9cb42c0ffdca69c1036330cd228a23366b666  round13/stage/v13a/adoption.tsv
c7b19e325e5232738d129073913be179f0317fb6  round13/stage/v13a/succession.tsv
e9bab6fdb2068815e3c401301a75b7c0826c77bd  round13/stage/v13a/decisions2.tsv
d0bd8ab93bcba557031b7faf9b9e68fca01e6e4a  round13/stage/v13a/MANIFEST.txt
2122d285bb170b3294b943e422fe08990899f9e3  round13/stage/v13a/TABLES.txt
c473e2bded1b07bf45946a987a93a18796733828  round13/stage/v13a/decisions2_nodes.tsv
c98d443e0fab9f6f843cd1777682ad6492172f45  round13/stage/v13a/nodes.count
b3b8bf6e032dfb4313581ac7e52249fbe2d3cb70  round13/stage/v13a/nodes_map.tsv
e49626a29314ae354ff481fcbf6b2e920995c6aa  round13/out/v13a/status.tsv
83f718aeea9691783c61957012531d6b1c9148ce  round13/out/v13a/certs.tsv
dd11650b6e763e95ea5c86a0a7dbec2ad9256059  round13/out/v13a/classes.tsv
3a21c90d84089f85df07849f1dc9be5de52bea61  round13/out/v13a/findings.tsv
186803ec1285e492a4b85fe7a9d466d424005d4f  round13/out/v13a/summary.tsv
824faa021cae88a827cf2bd7dd0884fd7cea762d  round13/out/v13a/RUN.txt
a9129b97edcbe249b4d60c9abbdf4ef8eca19dea  round12/out/v12a/status.tsv
d73464312f81f21161a3d0f96b3d1a420ba7c052  round12/out/v12a/certs.tsv
dd11650b6e763e95ea5c86a0a7dbec2ad9256059  round12/out/v12a/classes.tsv
b6320812ac501ed45ce4a4200f8cc39185b49b97  round12/out/v12a/findings.tsv
fdb058d502719f86e0a714febd4a49a396fe1268  round12/out/v12a/summary.tsv
939e911df776d0b5cc5a59bd502bf010a3ee971d  round12/out/v12a/RUN.txt
ce8654e67f324864b11bf2d7625e26ced1ddbe58  round12/stage/v12a/treatments.tsv
3570179eed68b9fad4a6755bbb63f83b9cf01532  round12/stage/v12a/treatment_witness.tsv
9fa4c19eb768086d470171032e04d9ba040ec06c  round12/stage/v12a/treatment_class.tsv
672dc16fef1f81eb13ce48a1e68e22be65ac997f  round12/stage/v12a/history.tsv
3f6c2bd03f6ab99f2a1cf41a53ffdebf94cf2fd2  round12/stage/v12a/history_anchor.tsv
4436d7215400eec2a8477dfac8b4220e93af23e8  round12/stage/v12a/history_claim.tsv
eb8a18d6c8889f7b8b10e1c31c075bb6f7a9fc3b  round12/stage/v12a/joined.tsv
58d76886e073fc92ed7be101c7a0692ec9721cbf  round12/stage/v12a/cert_text.tsv
f346de88331e5877693eaa3cdc6cdfdd3baf9c18  round12/stage/v12a/window_sha.tsv
096dfe40eafa0547d5a522a80bf3e65cbcead720  round12/stage/v12a/cite_index.tsv
8bfc2cbcfa7e87d4c0b2cd80efe4b68148545f13  round12/stage/v12a/history_bridge.tsv
ad3c33301d7ee8403d347345245527eaec13e1e2  round12/stage/v12a/part_zone.tsv
7d959452b3428dfb6c5a26971e573e238de7fd54  round12/stage/v12a/history_remand.tsv
88e9cb42c0ffdca69c1036330cd228a23366b666  round12/stage/v12a/adoption.tsv
c7b19e325e5232738d129073913be179f0317fb6  round12/stage/v12a/succession.tsv
e9bab6fdb2068815e3c401301a75b7c0826c77bd  round12/stage/v12a/decisions2.tsv
ad0aeedaad3032b4088a47a357578d26ef5605f2  round12/stage/v12a/TABLES.txt
85f9c29ef3f9509fd973b9dd3dde96c2e9df953c  round13/DESIGN13.md
27893f7dc4361e8818e72e1ee9fcd7c1dd3aab72  round13/certify13.py
d7bb1cf512b70199cdaef0d5a00b183e7efe9492  round13/certify13_claims.py
27ce1b77519fe27a9131c86713b036564dc2d33d  round13/freeze13.py
e105b59246fe645f02cedc0c9751cab27407b57a  round13/nodes13.py
59c25c28a938c413165b601f9bc973c8ea50cf97  round13/old_by_class13.py
1f5969f9e55c29ac97841fa7e582b7f6e1c0fbdf  round13/sealed_lines13.py
a37d4f8ba9242fd54885fbc7714d5600bb9e89fc  round13/shep_sealed13.py
820cd345ac7cce9c665d2ce02e97be9b1a8844b6  round13/stage13.py
c8f808cef8356e0ffa5e0a2e7a44ed86b28b26c9  round13/summary13.py
be75dac5d864d05486afe5dafcf6179e2291ae1e  round13/zones13.py
d1bb30b9e7af41fb66c41a5799c5cbcaa70f6dff  round13/clean13.sh
622273b66720dfb3df3dbccb14831ceb256dfecb  round13/score13.sh
e7c19c47ff3baa8c3fabe6cfd3dc12459f84b646  round13/score_sealed13.sh
f752defd6a4cbf4abb209568fcddb9fe6b8e3833  round13/agents/shadow13/alt13.py
6c80b35cdc6c756bb31bfa81f817933bc08b6dcd  round13/agents/shadow13/build13.py
149eaadce6a5638b2c9f8ab7a49136f6c1bd0aa3  round13/agents/shadow13/d13.py
323caeee3bc8dd921bdc9551a80dd4684c116b97  round13/agents/shadow13/nf13.py
69c96543eeddba48b4cf5897f7bf804c016e08a2  round13/audit/audit13lib.py
865fc57feb74b2c5813810cf4934b4b645da734a  round13/audit/make_packs13.py
8eccbb5193f6e791f8d98847822536d488cfc172  round13/audit/more_text13.py
c48d44e9532a7e3affe97f82de46ba6b12a86b6f  round13/audit/score_audit13.py
f57cd98a690c71fec43b866ef6ce252bb6cbc020  round13/audit/AUDITOR_BRIEF13.md
b6835f33deb6b93568171685d93af99b838de39c  round8/bench_h0/build_keys.py
0d0aa0045429545f5ada87a41bc05001e382e7e2  round8/bench_h0/diff_h0.py
6a4e3633599aecd17fd1be0b29049818a3cd4d9f  round8/bench_h0/score_h0.py
44eaad80d458454653beb7ff4afa74c96f96a5b8  round8/bench_h0/verify_h0.py
e36231f61ae2c9c71b61ccf6e324e41ec50a181e  round8/bench_h0/common/benchlib.py
deb57ea05d0d4442a4a925a49210037a1fee9f9e  round8/bench_h0/fjc_idb_appeals/score.py
47664ef7db3f3ae4b867768ec45be17bd765addb  round8/bench_h0/scdb_disposition/score.py
281fdd02e9e0b337f6b1247ee2a1bcaeb7620e47  round8/bench_h0/shadow_docket/score.py
a205b577cdf1ab7809a9ad071fc2f02bc8237808  round8/bench_h0/shadow_docket/sdlib.py
d952aa9080e34f24e94fb74755d3d95171e92b90  round8/bench_h0/state_overruled_tables/score.py
22ce26cb83daeef12ab629bb95f566552b47b622  round8/bench_h0/fjc_idb_appeals/key.tsv
79b98c57db2676e0a2146599cd3b2c1d680110ca  round8/bench_h0/fjc_idb_appeals/key_nodes.tsv
1caaba0938fae1bac1aaab02bccee0117ec1b789  round8/bench_h0/scdb_disposition/key.tsv
ae84c4a329ecbbd4d0be04649ea3e79cee72f1e7  round8/bench_h0/shadow_docket/key.tsv
daa566d94f0766d377a9d5975172b1feb68697fb  round8/bench_h0/state_overruled_tables/key.tsv
7bc7b98298eb47b5f47d12950b72a804fc676528  round7/score_fresh7.py
8b2ce0bb462e536b4100d6b1f4980ef999a8fe30  round7/score_hist_dev.py
3dd792c9c8e82c4e6a85583529943213f83ed44e  round6/shepardized/compare.py
c16db05b9a7cee5d139a531d9439ee316bab3b27  round5/gold_fresh/score_fresh.py
028904791961598205c47085f0eb872fb039596f  round5/tests/score_holdout.py
076e8b827ac98fffed7f8efe5b49bfaeee33ccdb  round5/tests/check_no_leak.py
51d66ee209d76d17d833797153894602feaa088f  round9/agents/calpart9/build_zones.py
a2e3996a7f103f28a2969b6299532cd2d080e986  round9/agents/calpart9/partzone.py
a30322842d4fd94870f82a0fa5ed83f0106fca9a  round9/agents/calpart9/partfix.py
21f12ac3d5be22f1d4b7d1f4870795d95b8c7d55  wsl/r13_run.sh
252a6a27d71e9574d1fbad8ddb95ef63e9b2c375  audit/statements.lock
f0de9b2f5debaff9e27cf326db06f40b13f79c40  benchmarks/common/benchlib.py
f960cad1681c65890e8c2ef3e7572abed9447195  benchmarks/shadow_docket/sdlib.py
a52c132044d65026a0cbd2d448a4134d221b3471  benchmarks/fjc_idb_appeals/score.py
063c00b040210104adc39246f4cc32714219e54c  benchmarks/shadow_docket/score.py
a6478dc7efb6703df9bb65091ec571ed58035c3f  benchmarks/scdb_disposition/score.py
e5c1ee870bdaa55c91750c117e1689c1e0142c20  benchmarks/state_overruled_tables/score.py
8db591e49103888a4540f376c5a186daf6c52918  benchmarks/songer_treat/score.py
1aa8f3f9b147ca4e97fef943913ac1a7664f3ef7  benchmarks/songer_treat/key.tsv
981c0bea600bb506e14720ec4e72474d3ca3750c  benchmarks/songer_treat/key_nodes.tsv
6284f28233d590e1b04e8654b9721d19c12f71cd  benchmarks/songer_treat/MAPPING.md
db892d361ffbe463410927d98dd85b6ff3436bcb  benchmarks/songer_treat/READY
32a4e75e3c35dfbf292927fb5c8e5259fc0d3981  benchmarks/brace_hall_state/score.py
1c7ee00044769764ad6308f3c3c6001da8c6eccf  benchmarks/brace_hall_state/key.tsv
d0c7d27c6eb5e03974966a598b45e2cf8fbafa17  benchmarks/brace_hall_state/key_nodes.tsv
f633f4102795bf0ecdf5fb332213660715f8445b  benchmarks/brace_hall_state/MAPPING.md
68469617123ecc8679d07fefb2a104d4794ce056  benchmarks/brace_hall_state/READY
96c218e99719de5bc7fe9021eddb479f43d220d7  benchmarks/fedcir_dataset/score.py
61d8f5105e5f22c71808ac09511d5d25f68f1304  benchmarks/fedcir_dataset/key.tsv
0868abdde86d054c829a421945ef737eeb5c5cbf  benchmarks/fedcir_dataset/key_nodes.tsv
c2ee038ad136ff24e314ad3e9965d9da6e0f76d5  benchmarks/fedcir_dataset/MAPPING.md
e5028843eb0b45cb97eace40501c2208244cbc62  benchmarks/fedcir_dataset/READY
847f0514022818512f54b4f0ca12cd0a5fed8666  benchmarks/bhk_enbanc/score.py
1111571a0f142c7e8a32253682dc86f8177b0c93  benchmarks/bhk_enbanc/key.tsv
13ea60f73748cd81756fde608c2d67f9ad7bfc28  benchmarks/bhk_enbanc/key_nodes.tsv
3b204a1209fc5b1d736562a4402e23f57941ee60  benchmarks/bhk_enbanc/MAPPING.md
ff8ba601e0de764dee7cd5088181ea64eb6279db  benchmarks/bhk_enbanc/READY
c9353b9424d1ec4fa38a5247e2ba25c703fb140a  benchmarks/fjc_idb_unpub/score.py
9357c91647cc6813ad798590d6c8cd48ed1df2f9  benchmarks/fjc_idb_unpub/key.tsv
820518dd860d56cafc0d18d85d178485473d7798  benchmarks/fjc_idb_unpub/key_nodes.tsv
43f1f25c4c4c8130fee70be58ee6df07e5602852  benchmarks/fjc_idb_unpub/MAPPING.md
55408ca55f88af6ec3766275cace2040dce36b8d  benchmarks/fjc_idb_unpub/READY
b86a1a0f92d6b555c41ee8d780ac04767803de55  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Audit.lean
5ad5cf74e59fcdc0cba44dadf9b7ae0e28db1170  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Basic.lean
faafc602c58b20e9bcde8bfdc7f07193b8ba1591  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Certificate.lean
c666f20bb1c8b6012961c4006b0dc26f645efb1f  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Core.lean
5b3507b7e4a8d68167e62a73e1961500e9825032  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Courts.lean
2fa46c5499fe7a42235175c2210175638f776e7f  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/CueTable.lean
87f6e51eab78785666368ccc44892c0ec5784566  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Data.lean
a02c1bc9f2a06b04b7a05a05328353ca61fa20a8  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Events.lean
8e32fdf51e20bc073f2db676e0093da191422a8e  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Examples.lean
d0582751e7849b48f2c55e28188608ece42a1928  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Holdings.lean
a675d15e34405cd58573f6e75d07dab1ea100e8f  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Hunt.lean
749532033dd8799e26384118da396b759b525884  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Mutants.lean
def3ba3d42f333060b3f61af7d6fd9442c78f981  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Registry.lean
54de5093d38d4482652790a1321746685e28f877  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Run.lean
4a74dab454fe120a1e7a7082c76abf746cd3a805  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Sha1.lean
24ac62e89b44759a0c23d6c2d1b2f03f1a7e3d5d  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Spec/Authority.lean
91ae32886870672bc8b0c19e988b1c3b0f142789  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Spec/AuthorityThms.lean
80bec6957610219e7425f68563745b31d21beb0f  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Spec/Findings.lean
8ff2d1c968d3ef24b7fff0fadcda8989af1f6602  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Spec/Horty.lean
ebd4a9418fd80fcda328ca973d0c4908d58bc7cc  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Spec/Lines.lean
0ed513fdfcf3e0d11fdf4f23fce91707c1dab94a  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Spec/Recognised.lean
bb92218236fcce1b1a724d05c343a144409ca888  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Spec/RuleId.lean
68245ddbefd799c5da220f54deae8f3e5506e7a8  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Spec/Splits.lean
a046aa687ca9c1e9d4f1423dfde6fff886ad9310  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Spec/Status.lean
64bc7cc13a0052918abc13086619998dafc431ac  ../../global-law-lean/lean-proofs/LegalProofs/CaseLaw2/Tsv.lean
24cac793f89ba201398a268fdfea5247e0f19d9e  ../../global-law-lean/lean-proofs/tools/caselaw2/cues/cue_table.json
absent  round13/stage/v13a/history_identity.tsv
```
