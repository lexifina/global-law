https://github.com/user-attachments/assets/152471be-a534-48f0-be6d-cdd98aacfa58

<p>Each case is a logical mistake in the law itself, laid out as a legal zero-day in the sense of <a href="https://arxiv.org/html/2508.10050v1">Legal Zero-Days: A Novel Risk Vector for Advanced AI Systems</a>: the rule, what the official text says, why the two don't fit, what follows, who could use it, and the strongest objections, each rated. We first present the categories of error by number; the five in-depth examples are linked under More.</p>

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
<li><a href="../MONITORING.md#vulnerability-scan-off-by-default">Monitoring</a>: how new law could be checked for these mistakes as it arrives</li>
<li><a href="scripts/">Scripts</a>: the detectors, the model review and the accuracy benchmark, with how often each step finds what it should</li>
</ul>

<h2>FAQ</h2>

<p><b>Are these real loopholes?</b> They are drafting mistakes confirmed against official sources, but none has been tested in court; this is theoretical research.</p>

<p><b>How were they found?</b> Detectors read the git history of 107 national law corpora in this repository, language models filtered the 74,000 flags, and the strongest survivors were checked by hand against gazettes and consolidated texts.</p>

<p><b>Can I report a correction?</b> Yes: open an issue in this repository with the provision and an official source.</p>
