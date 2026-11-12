https://github.com/user-attachments/assets/6f43621b-a186-4e16-9144-6946de279a03

<p>Each case is a logical mistake in the law itself, ranging from mechanical mistakes to <a href="https://arxiv.org/html/2508.10050v1">legal zero-days</a> (essentially loopholes). We present errors by category and frequency, provide five in-depth examples, and lay out an overall <a href="TAXONOMY.md">taxonomy</a> for finding legislative errors.</p>

<table>
<tr><th>Category</th><th>What it is</th><th>Flagged</th></tr>
<tr><td>Lapsed time limits</td><td>Text still applying a rule &quot;until&quot; a date that has passed</td><td>20,770</td></tr>
<tr><td>Repeal gaps</td><td>A provision repealed before its replacement took effect</td><td>15,876</td></tr>
<tr><td>Dead currencies</td><td>Amounts still stated in pesetas, marks, lire, cruzeiros and the like</td><td>8,394</td></tr>
<tr><td>References to repealed placeholders</td><td>Provisions pointing at a section that survives only as &quot;(repealed)&quot;</td><td>6,225</td></tr>
<tr><td>Same-day conflicts</td><td>Two amendments changing the same provision on the same day</td><td>6,161</td></tr>
<tr><td>Retroactive or pre-publication dates</td><td>Rules in force before they were made or published</td><td>5,769</td></tr>
<tr><td>Citations of repealed acts (Spain)</td><td>Laws in force citing acts that are no longer in force</td><td>2,925</td></tr>
<tr><td>Stale amounts</td><td>An amount changed in one place but not where it is repeated</td><td>2,361</td></tr>
<tr><td>Duplicate numbering</td><td>Two units with the same number in one provision</td><td>1,905</td></tr>
<tr><td>Empty periods</td><td>Time-limited rules extended only after they had run out</td><td>1,760</td></tr>
<tr><td>Missing paragraphs (Germany)</td><td>References to a paragraph that the cited section does not have</td><td>760</td></tr>
<tr><td>Failed amendments</td><td>Publisher notes that an amendment could not be carried out</td><td>524</td></tr>
<tr><td>References to deleted provisions</td><td>Provisions pointing at a section that no longer exists</td><td>451</td></tr>
<tr><td>Missing enabling power</td><td>Regulations citing a power that did not exist when they were made</td><td>197</td></tr>
<tr><td>Organic-law reserve (Spain)</td><td>Ordinary instruments changing an organic law</td><td>158</td></tr>
<tr><td>Dead fines (Germany)</td><td>Fine catalogues pointing at deleted sections</td><td>65</td></tr>
</table>

<h2>More</h2>

<ul>
<li><a href="EXAMPLES.md">5 in-depth examples</a>: the five mistakes walked through step by step, further confirmed mistakes, and empty periods</li>
<li><a href="data/confirmed.csv">Confirmed cases</a> (<a href="data/confirmed.json">JSON</a>): every case checked against official sources, with links</li>
<li><a href="data/">Full list of flags</a>: all of them as CSV, JSON Lines and Parquet, with counts <a href="data/by_category.csv">by category</a> and <a href="data/by_jurisdiction.csv">by jurisdiction</a>, the <a href="data/reviewed.csv">model-reviewed subset</a>, and <a href="data/html/index.html">browsable HTML pages</a></li>
<li><a href="../lean-proofs/">Formal proofs (Lean)</a>: the mistakes stated as theorems and checked by the Lean prover, with a certificate for every flag, plus a worked study of cliffs in the US tax code</li>
<li><a href="../monitoring/README.md#vulnerability-scan-off-by-default">Monitoring</a>: how new law could be checked for these mistakes as it arrives</li>
<li><a href="scripts/">Scripts</a>: the detectors, the model review and the accuracy benchmark, with how often each step finds what it should</li>
</ul>

<h2>FAQ</h2>

<p><b>Are these real loopholes?</b> They are drafting mistakes confirmed against official sources, but none has been tested in court; this is theoretical research.</p>

<p><b>How were they found?</b> Detectors read the git history of 107 national law corpora in this repository, language models filtered the 74,000 flags, and the strongest survivors were checked by hand against gazettes and consolidated texts.</p>

<p><b>Isn't a lot of this deliberate? Law is grey on purpose.</b> Often, yes. The detectors look for mechanical mistakes, not grey areas: a reference to a section that was repealed or renumbered, a fine that points at a deleted rule, a rule in force before it was published. Whether a gap is a mistake or a choice is a legal judgement, so every review gives a verdict, and most flags turn out to be lawful, cured, intended or errors in a corpus rather than defects in the law.</p>

<p><b>Courts read law by its purpose, history and case law. Isn't a check of the text alone dangerous?</b> Courts do read purpose, context and precedent, which is why each case lists the strongest objections and rates them, and why none is presented as settled. The cases shown are ones where that reading has least room, such as fines, which need an exact statutory basis. A flag is a prompt for a lawyer or a legislature to look, not legal advice. This repository also holds case law for many jurisdictions, so a flag can be checked against the decisions that apply it.</p>

<p><b>Doesn't version-controlled law already exist?</b> In places. legislation.gov.uk shows each UK act as it stood on any date, and the District of Columbia publishes its code on GitHub, where a resident once fixed a typo in the law with a pull request. Amending acts are already written as diffs ('insert ...', 'omit ...'). What is missing is coverage: the same versioned format for every jurisdiction, so the same checks run everywhere at once, and <code>git blame</code> shows which law wrote each word.</p>

<p><b>The law isn't software. Why apply software-style checks?</b> It isn't, and these checks do not try to prove a statute correct. They work like a linter: they catch the mechanical slips (references that point nowhere, impossible dates, amendments that could not be carried out) that drafters would fix if they saw them.</p>

<p><b>Who benefits, and will legislators ever adopt this?</b> It needs no one's adoption: published law is public, so anyone can run the checks. Finding these mistakes used to take legal training and time; publishing them puts pressure on legislatures to repair them, and lets everyone, not only well-advised insiders, see where the text fails.</p>

<p><b>Can I report a correction?</b> Yes: open an issue in this repository with the provision and an official source.</p>
