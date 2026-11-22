#!/usr/bin/env python3
"""Build the Financial Disclosure Intelligence site (5 episodes) from the
proven QM7073 engine (~/workspace/projects/qm7073-website/index.html).

Content source of truth: modules/ep1-5.json (lessons + checkpoint questions),
verified against SLIDES_EXTRACT.txt and FACT_SHEET.md in this folder.
Engine facts (from the QM template, unchanged):
- XP_LESSON = 10, XP_QUESTION = 20, XP_BONUS = 30 -> 120 XP/episode, 600 total.
- Stars = checkpoint score (var stars = state.score).
- Sequential unlocking via isUnlocked(); progress session-only (in-memory).
- Lesson "pages" -> paged mode; lesson.game (type 'build'/'sort') renders
  after the pages. One game per episode -> Game Master = finish it.
- Sort-game wrong-answer hint was hardcoded to QM wording; patched here to
  use g.hint when the game supplies one.
- Perfect-run bonus (+30) is awarded on ANY 3/3 completion, first clear or
  replay (QM engine gated it on firstClear, which capped the site at 570/600
  after a partial first clear); awardXP dedupes via state.awarded.
- Custom visuals (LM word-counter, FinBERT probability bar, ADAM result
  tables) are dispatched through renderVisual to window.FDI_* functions
  appended with this build; no external dependencies.
Do NOT push to GitHub from here; the coordinator handles the push.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path.home() / "workspace/projects/qm7073-website/index.html"
MOD = ROOT / "modules"

LEVELS = """var LEVELS = [
        { xp: 0, name: "Disclosure Rookie" },
        { xp: 120, name: "Paragraph Detective" },
        { xp: 240, name: "Tone Analyst" },
        { xp: 360, name: "Context Sleuth" },
        { xp: 480, name: "Adjudicator" },
        { xp: 600, name: "Disclosure Intelligence Master" }
      ];"""

HERO_ART = """<div class="hero-art" style="margin:0">
            <div class="hero-pipe" role="img" aria-label="The ADAM pipeline: six layers from disclosure to decision support">
              <span class="hp-step"><b>1</b> Disclosure &amp; Decision Context</span>
              <span class="hp-step"><b>2</b> Structuring &amp; Contextualization</span>
              <span class="hp-step"><b>3</b> Three Specialized Evidence Agents</span>
              <span class="hp-step gold"><b>4</b> Intelligent Adjudication</span>
              <span class="hp-step"><b>5</b> Disclosure Intelligence Synthesis</span>
              <span class="hp-step"><b>6</b> Decision-Support Outputs</span>
            </div>
            <figcaption>THE ADAM PIPELINE — 6 LAYERS FROM DISCLOSURE TO DECISION SUPPORT</figcaption>
          </div>"""

HQ_HTML = """<section id="hq">
        <div class="wrap">
          <div class="section-head">
            <h2>About ADAM &amp; Sources</h2>
            <p>The paper behind the game, the sources it stands on, and how to read its results honestly.</p>
          </div>
          <div class="hq-grid">
            <div class="hq-card wide-card">
              <h3>The episode map</h3>
              <p>Five episodes, played in sequence — each one unlocks the next. The first four teach the system; the fifth teaches the study.</p>
              <ul>
                <li><strong>Episode 1 — What Are Disclosures? The 10-K</strong> · What a 10-K is, Items 1 / 1A / 7 / 8, why 10-Ks are hard, ADAM's data</li>
                <li><strong>Episode 2 — The LM Dictionary</strong> · Loughran &amp; McDonald (2011), the six lists, the ~73.8% trap, the worked 50-word example</li>
                <li><strong>Episode 3 — FinBERT Reads Context</strong> · Araci (2019), softmax, argmax, confidence, the 0.62 worked example</li>
                <li><strong>Episode 4 — ADAM: Disagreement as Evidence</strong> · Six layers, three agents, adjudication, six discrepancy categories, preliminary results</li>
                <li><strong>Episode 5 — Our Research: The ADAM Study Itself</strong> · Four research questions, four design requirements, the human reference set, nested evaluation</li>
              </ul>
            </div>
            <div class="hq-card">
              <h3>The ADAM authors</h3>
              <p><strong>Kazim Topuz</strong> (presenter) · <strong>Jessica Bedson</strong> · <strong>Tally Ferguson</strong> · <strong>Thomas Kim</strong></p>
              <p>The University of Tulsa · DSI 2026</p>
              <p>Contact: <a href="mailto:Kazim-Topuz@utulsa.edu">Kazim-Topuz@utulsa.edu</a></p>
              <p>Core idea, in the authors' words: preserve disagreement, diagnose it, and turn it into decision-relevant evidence.</p>
            </div>
            <div class="hq-card">
              <h3>Your host</h3>
              <p><strong>Dr. K — Dr. Kazim Topuz</strong>, Associate Professor of Business Analytics and Operations Management at The University of Tulsa, hosts every episode, signs your badge certificates, and drops a field tip at the end of each lesson.</p>
            </div>
            <div class="hq-card wide-card">
              <h3>The big idea — three takeaways</h3>
              <div class="assign-grid">
                <div><strong>1 · Different models see different evidence</strong><p>Do not collapse that evidence too early. LM sees words; FinBERT sees sentences; context sees history and peers.</p></div>
                <div><strong>2 · Disagreement can be diagnostically useful</strong><p>Ask why methods diverge — and whether the conflict is resolvable. A disagreement with a diagnosis is evidence; without one, it is just noise.</p></div>
                <div><strong>3 · Decision support is more than accuracy</strong><p>Traceability, uncertainty, context, and human attention are part of the output. A system that hides its uncertainty is selling false precision.</p></div>
              </div>
            </div>
            <div class="hq-card wide-card">
              <h3>Sources</h3>
              <ul>
                <li><strong>Loughran &amp; McDonald (2011)</strong>, “When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks”, <em>Journal of Finance</em> 66(1), 35–65 — the finance-specific sentiment dictionary: Positive, Negative, Uncertainty, Litigious, Modal (strong/weak); Constraining joined later (Bodnaruk, Loughran &amp; McDonald, 2015).</li>
                <li><strong>Araci (2019)</strong>, “FinBERT: Financial Sentiment Analysis with Pre-trained Language Models”, arXiv:1908.10063 — BERT further pre-trained on finance text and fine-tuned on the Financial PhraseBank; an arXiv preprint / MSc thesis, not a peer-reviewed journal paper.</li>
                <li><strong>Bochkay, Brown, Leone &amp; Tucker (2023)</strong>, “Textual Analysis in Accounting: What's Next?”, <em>Contemporary Accounting Research</em> 40(2), 765–805 — survey and roadmap of NLP textual analysis in accounting, organising conventional vs ML / deep-learning methods.</li>
                <li><strong>Brown &amp; Tucker (2011)</strong>, “Large-Sample Evidence on Firms' Year-over-Year MD&amp;A Modifications”, <em>Journal of Accounting Research</em> 49(2), 309–348 — measures how much MD&amp;A changes year over year; MD&amp;A usefulness declines as boilerplate grows.</li>
                <li><strong>Hevner, March, Park &amp; Ram (2004)</strong>, “Design Science in Information Systems Research”, <em>MIS Quarterly</em> 28(1), 75–105 — the foundational design-science framework ADAM cites for its design-science framing (with Gregor &amp; Hevner, 2013).</li>
                <li><strong>SEC, “How to Read a 10-K/10-Q”</strong> — the structure of Items 1, 1A, 7, and 8 used in Episode 1 (sec.gov investor bulletin).</li>
              </ul>
            </div>
            <div class="hq-card">
              <h3>How to read the results</h3>
              <p>Every ADAM result on this site is labelled <strong>PRELIMINARY — VALIDATION ONGOING</strong>. The evaluation uses a 300-paragraph human reference set; confirmatory testing, confidence intervals, and paired significance tests are still to come in the final paper. Treat the numbers as the current validation picture, not as final claims.</p>
              <p>Probabilities in the FinBERT worked example (0.62 / 0.30 / 0.08) are <strong>illustrative teaching values, not a real model run</strong>. 10-K passages marked “illustrative paraphrase” are written in the style of a filing, not quoted from any company.</p>
            </div>
            <div class="hq-card">
              <h3>A note on the numbers</h3>
              <p>Slide 10 of the ADAM deck also prints “143,372 focal paragraphs”. The Item counts on the same slide sum to 179,623 (94,031 Item 1A + 85,592 Item 7), which is the figure used throughout this site. List sizes for the LM dictionary are approximate and version-dependent.</p>
              <p>The (Positive − Negative) ÷ (Positive + Negative) = −0.091 figure is <strong>Henry's (2008)</strong> tone measure, shown for comparison — it is not LM 2011's formula.</p>
            </div>
            <div class="hq-card wide-card">
              <h3>What you'll be able to do</h3>
              <div class="assign-grid">
                <div><strong>Navigate a 10-K</strong><p>Find Items 1, 1A, 7, and 8, and say what each one contains — and which two ADAM reads.</p></div>
                <div><strong>Count like LM</strong><p>Score a passage with the LM lists, compute % Positive, % Negative, and net tone, and name the formula that is not LM's.</p></div>
                <div><strong>Read FinBERT</strong><p>Turn a softmax distribution into a predicted class, a confidence, and a routing decision at the 0.80 threshold.</p></div>
                <div><strong>Adjudicate</strong><p>Separate tone, economic direction, and informativeness — and diagnose a disagreement instead of averaging it away.</p></div>
                <div><strong>Explain the study</strong><p>State the four research questions, the nested evaluation design, and why holding the adjudicator constant is the whole trick.</p></div>
              </div>
            </div>
            <div class="hq-card wide-card">
              <h3>Where it gets tricky — and why that's normal</h3>
              <div class="assign-grid">
                <div><strong>Words that look negative</strong><p>Tax, cost, capital, board, vice: a general dictionary flags them; finance does not. Always ask which dictionary produced a score.</p></div>
                <div><strong>Two formulas, one sign</strong><p>LM's net tone (−0.02) and Henry's measure (−0.091) agree on direction and disagree on magnitude. The formula matters as much as the words.</p></div>
                <div><strong>A clear label, a weak confidence</strong><p>FinBERT can say “Negative” at 0.62 confidence. The label is not the confidence — and below 0.80, ADAM sends it to a human.</p></div>
                <div><strong>Judge-only is already strong</strong><p>On sentiment and direction the LLM alone does most of the work. The architecture's proven gain is informativeness — say so honestly.</p></div>
                <div><strong>Humans disagree too</strong><p>Three careful reviewers agree unanimously only 21% of the time on sentiment. That is a fact about the task, not a failure of the study.</p></div>
              </div>
            </div>
            <div class="hq-card wide-card">
              <h3>About this site</h3>
              <p>A static, single-page practice companion for the ADAM paper (Topuz, Bedson, Ferguson &amp; Kim, University of Tulsa, DSI 2026). Nothing here is graded and nothing is uploaded: all progress (XP, stars, badges) lives in memory for this session only and resets when the page reloads. All interactive elements run in your browser with no external services.</p>
            </div>
          </div>
        </div>
      </section>"""

EXTRA_CSS = """
      /* ---------- FDI additions: hero pipeline, stat cards, tables, interactives ---------- */
      .hero-pipe{display:flex;flex-direction:column;gap:8px}
      .hero-pipe .hp-step{display:flex;align-items:center;gap:10px;background:var(--surface);border:2px solid var(--line);border-radius:12px;padding:10px 14px;font-weight:600;font-size:.98rem}
      .hero-pipe .hp-step b{display:grid;place-items:center;width:26px;height:26px;flex:none;border-radius:50%;background:var(--navy);color:var(--gold-bright);font-size:.85rem}
      .hero-pipe .hp-step.gold{border-color:var(--gold);background:var(--gold-soft)}
      .fdi-prelim{display:inline-block;background:var(--red-soft);color:var(--red);border:2px solid var(--red);border-radius:8px;padding:3px 10px;font-family:"Space Mono",monospace;font-weight:700;font-size:.75rem;letter-spacing:.08em;margin-bottom:10px}
      .viz-stats{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:6px}
      .viz-stat{background:var(--surface);border:2px solid var(--line);border-radius:12px;padding:12px;text-align:center}
      .viz-stat b{display:block;font-size:1.5rem;font-family:"Bricolage Grotesque",sans-serif}
      .viz-stat span{font-size:.85rem;color:var(--muted)}
      .fdi-table{width:100%;border-collapse:collapse;margin:8px 0 4px;font-size:.95rem}
      .fdi-table th,.fdi-table td{border:1px solid var(--line);padding:7px 10px;text-align:left}
      .fdi-table th{background:var(--bg-soft)}
      .fdi-table tr.hl td{font-weight:700;background:var(--gold-soft)}
      .fdi-note{font-size:.88rem;color:var(--muted);margin:6px 0 0}
      .lmw{display:inline-block;margin:2px;padding:4px 8px;border:2px solid var(--line);border-radius:999px;background:var(--surface);font:inherit;font-size:.92rem}
      .lmw:hover{border-color:var(--gold)}
      .lmw.sel-pos{background:var(--green-soft);border-color:var(--green);font-weight:700}
      .lmw.sel-neg{background:var(--red-soft);border-color:var(--red);font-weight:700}
      .lmw.sel-none{background:var(--bg-soft);border-color:var(--muted);color:var(--muted);text-decoration:line-through}
      .lmw:disabled{cursor:default}
      .fdi-score{background:var(--surface);border:2px solid var(--line);border-radius:12px;padding:12px 14px;margin-top:12px;font-family:"Space Mono",monospace;font-size:.92rem;line-height:1.8}
      .fdi-score b{color:var(--ink)}
      .fb-row{display:grid;grid-template-columns:88px 1fr 64px;gap:10px;align-items:center;margin:8px 0}
      .fb-row label{font-weight:700}
      .fb-row output{font-family:"Space Mono",monospace;font-weight:700;text-align:right}
      .fb-row input[type=range]{width:100%;accent-color:var(--gold)}
      .fb-bar{height:12px;border-radius:99px;background:var(--line);overflow:hidden;margin:2px 0 8px 98px}
      .fb-bar i{display:block;height:100%;background:var(--gold-bright)}
      .fb-bar.neg i{background:var(--red)}
      .fb-bar.pos i{background:var(--green)}
      .fb-verdict{margin-top:10px;padding:10px 14px;border-radius:12px;border:2px solid var(--gold);background:var(--gold-soft);font-weight:700}
      .fb-verdict.review{border-color:var(--red);background:var(--red-soft)}
"""

EXTRA_JS = """
      /* ============================================================
         FDI INTERACTIVES — LM word-counter, FinBERT probability bar,
         ADAM data / results visuals. Appended by build.py.
         ============================================================ */
      var FDI_WORDS = [
        ["Strong","pos"],["demand","none"],["helped","none"],["sales","none"],["improve","pos"],
        ["this","none"],["year,","none"],["and","none"],["efficient","pos"],["operations","none"],
        ["delivered","none"],["a","none"],["clear","none"],["benefit","pos"],["to","none"],
        ["shareholders.","none"],["Management","none"],["expects","none"],["continued","none"],["success","pos"],
        ["from","none"],["new","none"],["products.","none"],["However,","none"],["revenue","none"],
        ["faced","none"],["a","none"],["decline","neg"],["in","none"],["one","none"],
        ["segment,","none"],["a","none"],["loss","neg"],["on","none"],["discontinued","none"],
        ["operations,","none"],["and","none"],["higher","none"],["risk","neg"],["from","none"],
        ["volatility,","neg"],["leaving","none"],["the","none"],["outlook","none"],["weak","neg"],
        ["and","none"],["a","none"],["burden","neg"],["on","none"],["margins.","none"]
      ];
      function FDI_lmCounter(){
        var chips = FDI_WORDS.map(function(w, i){
          return '<button type="button" class="lmw" data-cls="' + w[1] + '" onclick="FDI_lmToggle(this)">' + w[0] + '</button>';
        }).join(" ");
        return '<div class="viz" role="group" aria-label="LM word counter">' +
          '<p style="margin-top:0"><strong>Try it yourself:</strong> click every word you think is on an LM list — Positive or Negative. The counts and scores recompute live. Words on neither list are marked, not counted.</p>' +
          '<div>' + chips + '</div>' +
          '<div class="fdi-score" id="fdi-lm-score">Positive: <b>0</b> &nbsp;·&nbsp; Negative: <b>0</b><br>%Pos: <b>0.0%</b> &nbsp;·&nbsp; %Neg: <b>0.0%</b><br>Net LM tone: <b>0.00</b> &nbsp;·&nbsp; Net per 1,000 words: <b>0</b></div>' +
          '<p class="fdi-note" id="fdi-lm-note">Total words: 50. Click words to score the passage.</p>' +
          '<div style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap">' +
          '<button type="button" class="btn btn-gold" onclick="FDI_lmReveal()">Reveal the answer</button>' +
          '<button type="button" class="btn btn-ghost" onclick="FDI_lmReset()">Reset</button></div></div>';
      }
      function FDI_lmScore(){
        var box = document.getElementById("fdi-lm-score"); if (!box) return;
        var pos = 0, neg = 0, wrong = 0;
        var chips = document.querySelectorAll("#p-stage .lmw");
        for (var i = 0; i < chips.length; i++){
          var c = chips[i];
          if (c.classList.contains("sel-pos")) pos++;
          else if (c.classList.contains("sel-neg")) neg++;
          else if (c.classList.contains("sel-none")) wrong++;
        }
        var pct = function(x){ return (x / 50 * 100).toFixed(1) + "%"; };
        var net = ((pos - neg) / 50);
        var netTxt = (net > 0 ? "+" : "") + net.toFixed(2);
        var per1k = Math.round((pos - neg) / 50 * 1000);
        box.innerHTML = "Positive: <b>" + pos + "</b> &nbsp;·&nbsp; Negative: <b>" + neg + "</b><br>" +
          "%Pos: <b>" + pct(pos) + "</b> &nbsp;·&nbsp; %Neg: <b>" + pct(neg) + "</b><br>" +
          "Net LM tone: <b>" + netTxt + "</b> &nbsp;·&nbsp; Net per 1,000 words: <b>" + (per1k > 0 ? "+" : "") + per1k + "</b>";
        var note = document.getElementById("fdi-lm-note");
        if (note){
          if (pos === 5 && neg === 6 && wrong === 0) note.textContent = "Exactly right: 5 positive, 6 negative — net LM tone −0.02 (−2.0%), −20 per 1,000 words.";
          else if (wrong > 0) note.textContent = "Careful: the struck-through words are on neither LM list — a dictionary would not count them.";
          else note.textContent = "Total words: 50. The lesson answer is 5 positive and 6 negative.";
        }
      }
      function FDI_lmToggle(btn){
        if (btn.disabled) return;
        var cls = btn.getAttribute("data-cls");
        if (btn.classList.contains("sel-pos") || btn.classList.contains("sel-neg") || btn.classList.contains("sel-none")){
          btn.classList.remove("sel-pos"); btn.classList.remove("sel-neg"); btn.classList.remove("sel-none");
        } else if (cls === "pos"){ btn.classList.add("sel-pos"); }
        else if (cls === "neg"){ btn.classList.add("sel-neg"); }
        else { btn.classList.add("sel-none"); }
        FDI_lmScore();
      }
      function FDI_lmReveal(){
        var chips = document.querySelectorAll("#p-stage .lmw");
        for (var i = 0; i < chips.length; i++){
          var c = chips[i], cls = c.getAttribute("data-cls");
          c.classList.remove("sel-pos"); c.classList.remove("sel-neg"); c.classList.remove("sel-none");
          if (cls === "pos") c.classList.add("sel-pos");
          else if (cls === "neg") c.classList.add("sel-neg");
        }
        FDI_lmScore();
      }
      function FDI_lmReset(){
        var chips = document.querySelectorAll("#p-stage .lmw");
        for (var i = 0; i < chips.length; i++){
          chips[i].classList.remove("sel-pos"); chips[i].classList.remove("sel-neg"); chips[i].classList.remove("sel-none");
        }
        FDI_lmScore();
      }
      function FDI_finbertBar(){
        return '<div class="viz" role="group" aria-label="FinBERT probability bar">' +
          '<p style="margin-top:0"><strong>Move the sliders</strong> to explore FinBERT\\u2019s output. The three numbers are normalized to sum to 1.00, the predicted class is the argmax, and the confidence is the max probability. Illustrative — not a live model run.</p>' +
          '<div class="fb-row"><label for="fdi-fb-n">Negative</label><input type="range" id="fdi-fb-n" min="0" max="100" value="62" oninput="FDI_fbUpdate()"><output id="fdi-fb-nv">0.62</output></div>' +
          '<div class="fb-bar neg"><i id="fdi-fb-nb" style="width:62%"></i></div>' +
          '<div class="fb-row"><label for="fdi-fb-u">Neutral</label><input type="range" id="fdi-fb-u" min="0" max="100" value="30" oninput="FDI_fbUpdate()"><output id="fdi-fb-uv">0.30</output></div>' +
          '<div class="fb-bar"><i id="fdi-fb-ub" style="width:30%"></i></div>' +
          '<div class="fb-row"><label for="fdi-fb-p">Positive</label><input type="range" id="fdi-fb-p" min="0" max="100" value="8" oninput="FDI_fbUpdate()"><output id="fdi-fb-pv">0.08</output></div>' +
          '<div class="fb-bar pos"><i id="fdi-fb-pb" style="width:8%"></i></div>' +
          '<div class="fdi-score" id="fdi-fb-score">P(Negative) = <b>0.62</b> &nbsp;·&nbsp; P(Neutral) = <b>0.30</b> &nbsp;·&nbsp; P(Positive) = <b>0.08</b> (sum 1.00)<br>Predicted class (argmax): <b>Negative</b> &nbsp;·&nbsp; Confidence (max probability): <b>0.62</b></div>' +
          '<div class="fb-verdict review" id="fdi-fb-verdict">Routes to human review — confidence 0.62 is below ADAM\u2019s 0.80 review threshold.</div></div>';
      }
      function FDI_fbUpdate(){
        var n = document.getElementById("fdi-fb-n"), u = document.getElementById("fdi-fb-u"), p = document.getElementById("fdi-fb-p");
        if (!n || !u || !p) return;
        var rn = +n.value, ru = +u.value, rp = +p.value, s = rn + ru + rp;
        var pn, pu, pp;
        if (s === 0){ pn = pu = pp = 1 / 3; } else { pn = rn / s; pu = ru / s; pp = rp / s; }
        var f2 = function(x){ return x.toFixed(2); };
        document.getElementById("fdi-fb-nv").textContent = f2(pn);
        document.getElementById("fdi-fb-uv").textContent = f2(pu);
        document.getElementById("fdi-fb-pv").textContent = f2(pp);
        document.getElementById("fdi-fb-nb").style.width = (pn * 100).toFixed(1) + "%";
        document.getElementById("fdi-fb-ub").style.width = (pu * 100).toFixed(1) + "%";
        document.getElementById("fdi-fb-pb").style.width = (pp * 100).toFixed(1) + "%";
        var cls = "Negative", conf = pn;
        if (pu > conf){ cls = "Neutral"; conf = pu; }
        if (pp > conf){ cls = "Positive"; conf = pp; }
        document.getElementById("fdi-fb-score").innerHTML =
          "P(Negative) = <b>" + f2(pn) + "</b> &nbsp;·&nbsp; P(Neutral) = <b>" + f2(pu) + "</b> &nbsp;·&nbsp; P(Positive) = <b>" + f2(pp) + "</b> (sum 1.00)<br>" +
          "Predicted class (argmax): <b>" + cls + "</b> &nbsp;·&nbsp; Confidence (max probability): <b>" + f2(conf) + "</b>";
        var v = document.getElementById("fdi-fb-verdict");
        if (conf >= 0.80){ v.className = "fb-verdict"; v.textContent = "Automated — confidence " + f2(conf) + " is at or above ADAM\\u2019s 0.80 review threshold."; }
        else { v.className = "fb-verdict review"; v.textContent = "Routes to human review — confidence " + f2(conf) + " is below ADAM\\u2019s 0.80 review threshold."; }
      }
      function FDI_adamData(){
        return '<div class="viz-stats">' +
          '<div class="viz-stat"><b>55</b><span>firms · 5 per GICS sector</span></div>' +
          '<div class="viz-stat"><b>11</b><span>GICS sectors</span></div>' +
          '<div class="viz-stat"><b>550</b><span>firm-year 10-Ks · 2016–2025</span></div>' +
          '<div class="viz-stat"><b>179,623</b><span>focal paragraphs</span></div></div>' +
          '<p class="fdi-note">94,031 from Item 1A + 85,592 from Item 7 = 179,623. Another 32,407 paragraphs (2014–2015) serve only as historical context.</p>';
      }
      function FDI_adamResults(){
        return '<div><span class="fdi-prelim">PRELIMINARY — VALIDATION ONGOING</span>' +
          '<table class="fdi-table"><tr><th>Method</th><th>Sentiment accuracy</th><th>Macro-F1</th></tr>' +
          '<tr><td>LM dictionary</td><td>37.3%</td><td>0.320</td></tr>' +
          '<tr><td>FinBERT</td><td>60.7%</td><td>0.529</td></tr>' +
          '<tr><td>LM–FinBERT ensemble</td><td>58.7%</td><td>0.384</td></tr>' +
          '<tr class="hl"><td>ADAM (current)</td><td>82.7%</td><td>0.745</td></tr></table>' +
          '<p class="fdi-note">Economic direction (ADAM): 83.3% accuracy, macro-F1 0.689. Disclosure informativeness (ADAM): 71.4% accuracy, macro-F1 0.607. Evaluated on the 300-paragraph human reference set; confirmatory testing still to come.</p></div>';
      }
      function FDI_adamDecision(){
        return '<div><span class="fdi-prelim">PRELIMINARY — VALIDATION ONGOING</span>' +
          '<table class="fdi-table"><tr><th>On the 162 paragraphs where LM ≠ FinBERT (54%)</th><th>Accuracy</th><th>Macro-F1</th></tr>' +
          '<tr><td>LM dictionary</td><td>25.3%</td><td>—</td></tr>' +
          '<tr><td>FinBERT</td><td>68.5%</td><td>0.606</td></tr>' +
          '<tr><td>LM–FinBERT ensemble</td><td>64.8%</td><td>—</td></tr>' +
          '<tr class="hl"><td>ADAM</td><td>76.5%</td><td>0.703</td></tr></table>' +
          '<p class="fdi-note">Where both base models were wrong (77 paragraphs), ADAM is correct on 89.6%. Decision support: High-informativeness flag 81.0% precision / 69.9% recall vs the FinBERT-negative rule at 19.5% precision. Confidence below 0.80 routes 56% to review, captures 92.3% of errors, and accuracy on the automated remainder is 97.0%.</p></div>';
      }
      function FDI_adamAblation(){
        return '<div><span class="fdi-prelim">PRELIMINARY — VALIDATION ONGOING</span>' +
          '<table class="fdi-table"><tr><th>Configuration (same adjudicator)</th><th>Sentiment</th><th>Direction</th><th>Informativeness</th></tr>' +
          '<tr><td>Judge-only (paragraph only)</td><td>82.0% / .731</td><td>84.0% / .683</td><td>67.2% / .453</td></tr>' +
          '<tr><td>Base evidence (+ LM + FinBERT)</td><td>82.0% / .730</td><td>83.7% / .694</td><td>68.3% / .469</td></tr>' +
          '<tr class="hl"><td>Full ADAM (+ Context &amp; Quality)</td><td>82.7% / .745</td><td>83.3% / .689</td><td>71.4% / .607</td></tr></table>' +
          '<p class="fdi-note">Accuracy / macro-F1. Informativeness ΔF1: +.138 vs Base, +.154 vs Judge-only — both statistically significant. But note the honest boundary: Judge-only already reaches 82.0% on sentiment and 84.0% on direction, slightly above Full ADAM\\u2019s 83.3% — the architecture\\u2019s proven gain is informativeness.</p></div>';
      }
"""

def load_episodes():
    eps = []
    for n in range(1, 6):
        ep = json.loads((MOD / f"ep{n}.json").read_text())
        assert ep["n"] == n
        assert len(ep["lessons"]) == 3 and len(ep["quiz"]) == 3, ep["n"]
        for q in ep["quiz"]:
            assert len(q["opts"]) == 4 and 0 <= q["a"] < 4 and q["why"], (n, q)
        # Page every lesson (one paragraph per page); game on lesson 3.
        for li, L in enumerate(ep["lessons"]):
            L["pages"] = [{"h": L["h"], "body": [p]} for p in L["body"]]
            for key in ("visual", "visual2", "visual3"):
                if key in L:
                    L["pages"][L[key + "_page"]]["visual"] = L[key]
        eps.append(ep)
    return eps

def main():
    eps = load_episodes()
    t = SRC.read_text()
    # 1. Episodes
    i = t.index("var EPISODES = [")
    j = t.index("var BOSSES", i)
    t = t[:i] + "var EPISODES = " + json.dumps(eps, ensure_ascii=False) + ";\n        " + t[j:]
    # 2. Bosses: none in this 5-episode site; remove trail insertions.
    i = t.index("      var BOSSES = {")
    j = t.index("      var LEVELS", i)
    t = t[:i] + "      var BOSSES = {};\n\n" + t[j:]
    t = t.replace('          if (i === 4) html += bossHTML("after5");\n', "")
    t = t.replace('          if (i === 7) html += bossHTML("after8");\n', "")
    assert "after5" not in t and "after8" not in t
    # Remove the now-dead bossHTML function (it carries "Boss Battle" copy).
    t2, nsub = re.subn(r'      function bossHTML\(key\)\{.*?\n      \}\n', '', t, flags=re.S, count=1)
    assert nsub == 1, f"bossHTML removal: {nsub}"
    t = t2
    assert "bossHTML" not in t
    # 3. Levels (600 XP max)
    i = t.index("      var LEVELS = [")
    j = t.index("      var XP_LESSON", i)
    t = t[:i] + LEVELS + "\n" + t[j:]
    # 4. Sort-game hint: use the game's own hint when supplied (QM wording was hardcoded).
    # 4b. HUD cleared-count was hardcoded to 8 in the QM engine; make it dynamic.
    old_hud = '        $("hud-cleared").textContent = clearedCount + " / 8 cleared";'
    assert old_hud in t, "HUD cleared line not found"
    t = t.replace(old_hud,
        '        $("hud-cleared").textContent = clearedCount + " / " + EPISODES.length + " cleared";')
    old_hint = ('          var hint = g.buckets.length === 2\n'
                '            ? "Not quite — is it a recorded fact, or meaning that can change a decision?"\n'
                '            : "Not quite — what happened, what will happen, or what should we do?";')
    assert old_hint in t, "sort hint block not found"
    t = t.replace(old_hint,
        '          var hint = g.hint || (g.buckets.length === 2\n'
        '            ? "Not quite — is it a recorded fact, or meaning that can change a decision?"\n'
        '            : "Not quite — what happened, what will happen, or what should we do?");')
    # 4c. Perfect-run bonus (VERIFICATION_REPORT §3.1, blocking): the QM engine
    # awards the +30 bonus only inside `if (firstClear)`, so an episode first
    # cleared imperfectly could never earn it on replay (site capped 570/600).
    # Move the award out of the firstClear block; awardXP already dedupes via
    # state.awarded, so it totals exactly +30 once per episode. The results
    # line must claim the bonus only when it was actually awarded this run.
    old_bonus = ('      function renderResults(ep){\n'
                 '        var firstClear = !state.cleared[state.current];\n'
                 '        var stars = state.score;\n'
                 '        if (firstClear){\n'
                 '          state.cleared[state.current] = true;\n'
                 '          if (state.score === ep.quiz.length) awardXP("B" + state.current, XP_BONUS);\n'
                 '        }\n')
    assert old_bonus in t, "renderResults bonus block not found"
    t = t.replace(old_bonus,
        '      function renderResults(ep){\n'
        '        var firstClear = !state.cleared[state.current];\n'
        '        var stars = state.score;\n'
        '        if (firstClear){\n'
        '          state.cleared[state.current] = true;\n'
        '        }\n'
        '        // Perfect-run bonus: awarded on ANY 3/3 completion, first clear or replay.\n'
        '        // awardXP dedupes via state.awarded, so this totals exactly +30 once per episode.\n'
        '        var bonusAwarded = false;\n'
        '        if (state.score === ep.quiz.length && !state.awarded["B" + state.current]){\n'
        '          awardXP("B" + state.current, XP_BONUS);\n'
        '          bonusAwarded = true;\n'
        '        }\n')
    old_bonus_line = ("          '<div class=\"score-line\">Checkpoint score: ' + state.score + ' / ' + ep.quiz.length + (state.score === ep.quiz.length ? ' · Perfect-run bonus +' + XP_BONUS + ' XP' : '') + '</div>' +\n")
    assert old_bonus_line in t, "perfect-run bonus display line not found"
    t = t.replace(old_bonus_line,
        "          '<div class=\"score-line\">Checkpoint score: ' + state.score + ' / ' + ep.quiz.length + (bonusAwarded ? ' · Perfect-run bonus +' + XP_BONUS + ' XP' : '') + '</div>' +\n")
    # 4d. Certificate placeholder: the QM template's hidden overlay still says
    # "Framing Badge" (no such badge exists here). Neutral default; openCert
    # overwrites it with the episode badge at open time.
    old_cert = '          <div class="c-badge" id="cert-badge">Framing Badge</div>'
    assert old_cert in t, "cert-badge placeholder not found"
    t = t.replace(old_cert, '          <div class="c-badge" id="cert-badge">Episode Badge</div>')
    # 5. renderVisual: dispatch FDI visuals to the appended functions.
    anchor = ('        if (key === "sentence") return \'<div class="viz viz-sent">Should <b>owner</b> <b>decision</b>, choosing among <b>alternatives</b>, judged on <b>criteria</b>?</div>\';')
    assert t.count(anchor) == 1, "renderVisual anchor not found"
    t = t.replace(anchor, anchor + "\n"
        '        if (key === "adam-data") return window.FDI_adamData();\n'
        '        if (key === "lm-counter") return window.FDI_lmCounter();\n'
        '        if (key === "finbert-bar") return window.FDI_finbertBar();\n'
        '        if (key === "adam-results") return window.FDI_adamResults();\n'
        '        if (key === "adam-decision") return window.FDI_adamDecision();\n'
        '        if (key === "adam-ablation") return window.FDI_adamAblation();')
    # 6. Branding / hero / how-to / footer / certificate
    reps = [
        ("<title>Foundations of Analytics — The Analytics Quest | QM 7073</title>",
         "<title>Financial Disclosure Intelligence — From Model Disagreement to Disclosure Intelligence | ADAM</title>"),
        ("Foundations of Analytics<small>QM 7073 · The Analytics Quest</small>",
         "Financial Disclosure Intelligence<small>ADAM · University of Tulsa · DSI 2026</small>"),
        ("Level 1 · Data Cadet", "Level 1 · Disclosure Rookie"),
        ("0 / 8 cleared", "0 / 5 cleared"),
        ("Season 1 · 8 Episodes · Graduate Course", "DSI 2026 · 5 Episodes · Micro-learning"),
        ("Foundations of Analytics:<br /><span class=\"quest\">The Analytics Quest</span>",
         "Financial Disclosure Intelligence:<br /><span class=\"quest\">From Model Disagreement to Disclosure Intelligence</span>"),
        ("QM 7073 at The University of Tulsa, played like a game. Each episode teaches a core analytics concept in <strong>bite-size micro-lessons</strong>, then challenges you with checkpoint questions before you can move on. Clear all eight episodes, survive two boss battles, and level up from Data Cadet to Analytics Master.",
         "ADAM — an agentic decision-support system for financial narratives — played like a game. Each episode teaches one piece of the system in <strong>bite-size micro-lessons</strong>, then challenges you with checkpoint questions before you can move on. Clear all five episodes and level up from Disclosure Rookie to Disclosure Intelligence Master."),
        ("Course HQ &amp; Syllabus", "About ADAM &amp; Sources"),
        ("8-week online course", "5 episodes · 600 XP total"),
        ("Evans, <em>Business Analytics</em>, 3rd ed.", "Based on the ADAM paper · Topuz et al., DSI 2026"),
        ("Prereq: QM 2013 (C or higher)", "No prerequisites — just curiosity"),
        ("Three questions per episode with instant feedback and explanations — the same style as the course Knowledge Checks in MyLab.",
         "Three questions per episode with instant feedback and a full explanation for every answer."),
        ("Earn XP for every lesson and correct answer, collect a badge per episode, and climb from Data Cadet to Analytics Master.",
         "Earn XP for every lesson and correct answer, collect a badge per episode, and climb from Disclosure Rookie to Disclosure Intelligence Master."),
        ("Step 4 · Boss battles", "Step 4 · Think like ADAM"),
        ("<h3>Midterm &amp; Final</h3>", "<h3>Diagnose disagreement</h3>"),
        ("The Midterm guards the trail after Episode 5 (Modules 1–5); the Final waits at the end (Modules 6–8). 150 points each.",
         "Disagreement is a clue, not noise. Learn why two good methods diverge — and whether the conflict is resolvable."),
        ("Checkpoint cleared — but this boss deserves a rematch. Replay to earn more stars.",
         "Checkpoint cleared — but this one deserves a rematch. Replay to earn more stars."),
        ("<span><strong>QM 7073 · Foundations of Analytics</strong> — Collins College of Business, The University of Tulsa</span>",
         "<span><strong>Financial Disclosure Intelligence</strong> — based on ADAM (Topuz, Bedson, Ferguson &amp; Kim, University of Tulsa, DSI 2026)</span>"),
        ("Full syllabus and grades live in Harvey and Pearson MyLab.",
         "Progress is session-only and resets on reload. All ADAM results are preliminary — validation ongoing."),
        ("<div class=\"c-kicker\">QM 7073 · Foundations of Analytics</div>",
         "<div class=\"c-kicker\">Financial Disclosure Intelligence · ADAM</div>"),
        ("A QM 7073 Quest player", "A Disclosure Intelligence player"),
        ("Dr. K — Dr. Kazim Topuz<br><small>QM 7073 Foundations of Analytics · University of Tulsa</small>",
         "Dr. K — Dr. Kazim Topuz<br><small>Financial Disclosure Intelligence · University of Tulsa</small>"),
        ("Practice companion — graded work lives in Harvey and Pearson MyLab.",
         "Practice companion — progress is session-only. All ADAM results are preliminary."),
    ]
    for old, new in reps:
        if old not in t:
            print("WARN: not found:", old[:90], file=sys.stderr)
        t = t.replace(old, new)
    # 7. Hero art -> ADAM pipeline (no external image asset)
    t2, nsub = re.subn(r'<figure class="hero-art".*?</figure>', HERO_ART, t, flags=re.S)
    assert nsub == 1, f"hero figure replacements: {nsub}"
    t = t2
    # 8. HQ section wholesale
    i = t.index('<section id="hq">')
    j = t.index("      <footer>", i)
    t = t[:i] + HQ_HTML + "\n\n" + t[j:]
    # 9. Appended CSS + JS
    assert t.count("</style>") == 1
    t = t.replace("</style>", EXTRA_CSS + "    </style>", 1)
    assert "</body>" in t
    t = t.replace("</body>", "    <script>" + EXTRA_JS + "    </script>\n  </body>", 1)
    # 10. Safety checks
    for bad in ["QM 7073", "MyLab", "Evans", "Data Cadet", "Analytics Master",
                "Analytics Quest", "after5", "after8", "8-week", "8 Episodes",
                "eight episodes", "Boss Battle", "Boss battles", "Midterm",
                "Final Exam", "150 PTS", "IN MYLAB", "quest-map", "Harvey",
                "150 points", "boss deserves", "Framing Badge"]:
        assert bad not in t, f"leftover: {bad}"
    assert "stars = state.score" in t, "star rule"
    assert "XP_LESSON = 10, XP_QUESTION = 20, XP_BONUS = 30" in t
    assert 3 * 10 + 3 * 20 + 30 == 120 and 5 * 120 == 600
    assert t.count("143,372") == 7, f"143,372 count: {t.count('143,372')}"  # lesson bodies appear twice (body + pages): Ep1 L3 x2, Ep5 L2 x2, Ep1 Q2 opt + why, HQ note
    assert "PRELIMINARY — VALIDATION ONGOING" in t
    assert t.count("PRELIMINARY — VALIDATION ONGOING") >= 5, t.count("PRELIMINARY — VALIDATION ONGOING")
    (ROOT / "index.html").write_text(t)
    print(f"built {ROOT / 'index.html'} ({len(t)} bytes, 5 episodes, 600 XP max)")

if __name__ == "__main__":
    main()
