# ADAM — Verified Fact Sheet (research only, not the website)

Scope: verifies the brief's facts against `SLIDES_EXTRACT.txt` (slides cited as S#) and external sources (URLs). No invented numbers/quotes. `UNVERIFIED` = could not be confirmed in this research.

## 1. SEC Form 10-K — structure, who files, deadlines

- **What it is:** annual report most U.S. public companies must file each year with the SEC; company-written, SEC sets the topics, fixed order of items; free on EDGAR. CEO/CFO must certify accuracy. Source: https://www.sec.gov/oiea/investor-alerts-and-bulletins/how-read-10-k10-q
- **Item 1 — Business:** main products/services, subsidiaries, markets; also recent events, competition, regulation, labour, operating costs, seasonality. (SEC bulletin, as above)
- **Item 1A — Risk Factors:** most significant risks to the company/securities, generally listed in order of importance; focuses on the risks themselves, not how the company addresses them. Risks may be economy-wide, industry/region, or firm-unique. (SEC bulletin)
- **Item 7 — MD&A:** management's own-words perspective on the past year: operations/results, liquidity & capital resources, known trends/uncertainties, material period-over-period changes, critical accounting judgments/estimates. (SEC bulletin)
- **Item 8 — Financial Statements & Supplementary Data:** audited statements — income statement, balance sheets, statement of cash flows, statement of stockholders' equity — plus explanatory notes; prepared under GAAP, audited by an independent accountant (unqualified opinion = fairly presented). (SEC bulletin)
- **Deadlines (Form 10-K, General Instruction A / 17 CFR 249.310):** 60 days after fiscal year-end (large accelerated filers, public float ≥ $700m), 75 days (accelerated filers), 90 days (all other registrants). Source: https://www.ecfr.gov/api/renderer/v1/content/enhanced/2025-01-30/title-17?chapter=II&part=249&subpart=D&section=249.310 ; also https://www.mayerbrown.com/-/media/files/perspectives-events/publications/2025/12/2026-sec-filing-deadlines-and-financial-statement-staleness-dates.pdf%3Frev=-1
- **Typical passages — ILLUSTRATIVE PARAPHRASES, not company quotes** (no exact company quote was verified in this research; do not present these as quotes):
  - *Item 1A-style:* "Our business faces risks that could cause actual results to differ materially from expectations, including competition, supply disruption, regulation, and litigation." (Paraphrase of the SEC bulletin's description.)
  - *Item 7-style:* "Revenue rose this year because volumes increased, partly offset by higher costs; liquidity remains adequate, but a known trend in input prices could affect future margins." (Paraphrase of MD&A content per SEC bulletin; SEC gives only generic examples, e.g. a manufacturer discussing commodity risk, a bank discussing liquidity under a rate rise — same source.)
  - To use a real quote, pull it from a named filing on EDGAR and cite filing + accession no. — not done here.

## 2. Loughran & McDonald (2011) dictionary

- **Paper:** Loughran & McDonald, "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks", *Journal of Finance* 66(1), 35–65. Lists: https://sraf.nd.edu/loughranmcdonald-master-dictionary/ (updated Mar 2026; free for academic research).
- **Lists (2011 original, approx. — counts vary by version/counting rule, see note):** Positive ~354, Negative ~2,337–2,355, Uncertainty ~297, Litigious ~904, Strong Modal 19, Weak Modal 27. Constraining ~184 is a **later** addition (Bodnaruk, Loughran & McDonald 2015, financial constraints), not in the 2011 six. Sources: RBI table reproducing LM 2011 counts (354/2,355/297/904/19/27/184) https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=19431 ; 2,337-word Fin-Neg figure in LM summary https://github.com/jonx0037/sentiment-regime-detector/blob/HEAD/course_files/research/summaries/loughran-mcdonald-2011-when-is-a-liability-not-a-liability-textual-analysis-dictionaries-and-10-ks-the-journal-of-finance_ScholarcySummary.md ; current (2025) master file counted at 2,345 Neg / 347 Pos / 297 Unc / 903 Lit / 19 / 27 / 184 — https://rillor.com/insights/financial-sentiment-dictionaries-finbert-llms/report . **Site must say "approx., version-dependent", not exact.**
- **Why general dictionaries fail (LM 2011):** ~73.8% (nearly three-fourths) of Harvard-IV negative word counts in 10-Ks are words not negative in finance — e.g. *tax, cost, capital, liability, board, vice*; also *mine, cancer, crude* mark an industry, not an event. Sources: LM abstract via RBI link above; https://www.formalnlp.com/topics/lexicon-sentiment-loughran-mcdonald . Note: in LM's own list, *liability, litigation, risk* **are** Negative — the point is Harvard mislabels them *in context*, LM re-classifies deliberately for finance.
- **Formulas — distinguish carefully:**
  - **LM 2011's own measures are proportions:** % Positive = Pos / total words; % Negative = Neg / total words (same for Uncertainty etc.). Net LM tone = (Pos − Neg) / total words. Source: https://WWW.FEDERALRESERVE.GOV/econres/feds/files/2024085pap.pdf ("count positive… subtract negative… divided by the number of all words").
  - **(Pos − Neg)/(Pos + Neg), range −1 to +1, is NOT LM 2011's formula** — it is Henry (2008)'s tone measure, widely used *with* LM lists. Source: https://afajof.org/management/viewp.php?n=198884 (attributes formula to Henry 2008).
  - **Per-1,000-words tone** = (count / total words) × 1,000 — a rescaling of the proportional measure, not a separate LM formula.
  - LM also use a negation rule: a positive word preceded within 3 words by *no/not/none/neither/never/nobody* is reclassified negative (per LM 2011, via https://skills.himanshujangir.com/skills/earnings-call-transcript-nlp-signal-research/ — secondary source; treat as standard practice, not directly verified against the paper here).
- **WORKED EXAMPLE (hand-countable, 50 words).** Passage (10-K-style, invented for teaching):
  > "Strong demand helped sales improve this year, and efficient operations delivered a clear benefit to shareholders. Management expects continued success from new products. However, revenue faced a decline in one segment, a loss on discontinued operations, and higher risk from volatility, leaving the outlook weak and a burden on margins."
  - Word membership verified in published LM subset lists: Positive — *strong, improve, efficient, benefit, success*; Negative — *decline, loss, risk, volatility, weak, burden*. Source for each classification: https://www.acctlab.app/bonus/power-query-NLP/ (lists improve/efficient/benefit/success/strong as Positive; decline/loss/risk/volatility/weak/burden as Negative). No other word in the passage is in either list (check: *demand, sales, year, operations, shareholders, management, expects, continued, products, revenue, segment, discontinued, higher, outlook, margins* — none listed as Pos/Neg in that source; *expects* is not an LM Positive word — do not count it).
  - Counts: total words N = 50; Positive = 5; Negative = 6. (Counted token by token; "operations" appears twice, neither is a list word.)
  - LM proportional: %Pos = 5/50 = 10.0%; %Neg = 6/50 = 12.0%; net tone (LM) = (5−6)/50 = **−0.02 (−2.0%)**.
  - Per 1,000 words: Pos = 5/50×1,000 = **100**; Neg = 6/50×1,000 = **120**; net = **−20 per 1,000 words**.
  - Henry tone (for comparison, not LM): (5−6)/(5+6) = −1/11 = **−0.091**. Sign: net negative in all three — consistent, magnitudes differ, which is the teaching point.

## 3. FinBERT (Araci 2019)

- **Paper:** Araci, D. (2019), *FinBERT: Financial Sentiment Analysis with Pre-trained Language Models*, arXiv:1908.10063 (MSc thesis, Univ. of Amsterdam, 25 Jun 2019). https://arxiv.org/abs/1908.10063 — note: arXiv preprint/thesis, **not a peer-reviewed journal venue**. ProsusAI model card: https://huggingface.co/ProsusAI/finbert/blob/main/README.md
- **What it is:** BERT-base (12 layers, 768 hidden, 12 heads) further pre-trained on a Reuters TRC2 financial subset, then fine-tuned for sentiment on **Financial PhraseBank** (Malo et al. 2014, 4,845 sentences, 28.1% Pos / 12.4% Neg / 59.4% Neu overall; 2,262 with 100% annotator agreement) + FiQA Task 1. Reported: 0.86 accuracy / 0.84 F1 on all PhraseBank data; 0.97 / 0.95 on the 100%-agreement subset. Sources: arXiv paper (http://arxiv.org/pdf/1908.10063v1) and HF card above.
- **Output:** softmax over 3 classes {positive, negative, neutral}; predicted class = argmax; confidence = max probability. (HF card: "The model will give softmax outputs for three labels: positive, negative or neutral.")
- **WORKED EXAMPLE.** Sentence: "Revenue fell sharply as costs rose and demand weakened." Suppose FinBERT returns:
  - P(Negative) = 0.62, P(Neutral) = 0.30, P(Positive) = 0.08. Check: 0.62+0.30+0.08 = **1.00** ✓.
  - Predicted class = argmax = **Negative** (0.62 is largest). Confidence = max probability = **0.62**.
  - Teaching note: 0.62 is a *weak* confidence — under ADAM's S18 routing threshold (confidence < 0.80 → review), this paragraph would go to human review. (Probabilities here are illustrative teaching values, not a real model run — label them as such on the site.)

## 4. Slide-number reconciliation (SLIDES_EXTRACT.txt)

- **S10 VERDICT — USE 179,623. The "143,372" figure is inconsistent and must not be used.**
  - Headline: "179,623 focal paragraphs"; table: Item 1A 94,031 + Item 7 85,592 = **179,623** ✓ (94,031+85,592 = 179,623, verified by arithmetic). The table's own "143,372 focal paragraphs" contradicts both.
  - 179,623 − 143,372 = 36,251, which matches nothing in the slide: historical 2014–2015 context = 32,407 paragraphs (179,623+32,407 = 212,030 total incl. history). So 143,372 is not explained by excluding history either.
  - Supporting checks pass: 55 firms = 5 per sector × 11 GICS sectors; 55 × 10 years (2016–2025) = 550 firm-years ✓ (S10 notes).
  - **Site should use: 179,623 focal paragraphs (94,031 Item 1A + 85,592 Item 7); 55 firms; 11 sectors; 550 firm-years; 32,407 historical-context paragraphs (2014–2015). Flag 143,372 as a slide error to be corrected with MK.**
- **All other ADAM numbers cross-checked — NO other mismatch found:**
  - S11: 144 Item 1A + 156 Item 7 = 300 ✓. S12: agreement rows each sum to 100% (21+66+13; 25+64+11; 32+54+14) ✓.
  - S14 sentiment: LM 37.3% / F1 0.320; FinBERT 60.7% / 0.529; Ensemble 58.7% / 0.384; ADAM 82.7% / 0.745 ✓ (consistent with S17 Full ADAM row).
  - S15: Direction 83.3% / F1 0.689 / P 0.757 / R 0.647; Informativeness 71.4% / 0.607 / 0.631 / 0.649 ✓ (match S17).
  - S16: disagreement 162/300 = 54% ✓; ADAM on disagreement 76.5% / F1 0.703 vs FinBERT 68.5% / 0.606, LM 25.3%, Ensemble 64.8% ✓; both-wrong cases 77, ADAM correct 89.6% → 0.896×77 = 69.0, i.e. 69/77 = 89.6% ✓.
  - S17 ablation deltas: Info F1 0.607−0.469 (Base) = **+0.138**; 0.607−0.453 (Judge-only) = **+0.154** ✓ exactly as stated.
  - S18: High-info flag P 81.0% / R 69.9% vs FinBERT-negative rule 19.5% ✓; routing: 56% of 300 = 168 to review; sentiment errors ≈ 300×(1−0.827) ≈ 52; 92.3% captured ≈ 48; remainder 132 at 97.0% ≈ 4 errors; 48+4 = 52 ✓ (rounding-consistent).
  - **Nuance, not an error:** S17 Judge-only beats Full ADAM on direction accuracy (84.0% vs 83.3%) and ties on sentiment (82.0% vs 82.7%) — site must not claim ADAM wins everywhere; the architectural gain is informativeness only, per S17 notes.

## 5. Cited papers — one-line verified descriptions

- **Bochkay, Brown, Leone & Tucker (2023), "Textual Analysis in Accounting: What's Next?", *Contemporary Accounting Research* 40(2), 765–805, doi:10.1111/1911-3846.12825** — survey/roadmap of NLP textual analysis in accounting (sentiment, readability, quantity, similarity, forward-looking info, themes), organising conventional vs ML/deep-learning methods and urging more deep-learning use. Source: https://www.kellogg.northwestern.edu/academics-research/research/detail/2023/textual-analysis-in-accounting-whats-next/
- **Brown & Tucker (2011), "Large-Sample Evidence on Firms' Year-over-Year MD&A Modifications", *Journal of Accounting Research* 49(2), 309–348** — measures how much MD&A changes year over year (modification score from document length/similarity); firms with bigger economic changes modify more, and MD&A usefulness declines as boilerplate grows. Source: https://eaa-online.org/app/uploads/sites/67/2021/09/EAA-2015-PhD-Forum-Presentation-Steven-Young.pdf (citation) + https://par.nsf.gov/servlets/purl/10087126 (modification-score description).
- **Hevner, March, Park & Ram (2004), "Design Science in Information Systems Research", *MIS Quarterly* 28(1), 75–105** — foundational design-science framework: seven guidelines for building/evaluating IT artifacts (incl. DSS) as rigorous research; ADAM cites it for its design-science framing (S19, with Gregor & Hevner 2013). Source: https://ailab-ua.github.io/courses/MIS611D/hevner-2004-design_science_in_is_research.pdf

## 6. UNVERIFIED / needs MK or primary-source check

- Exact LM 2011 list sizes (2,337 vs 2,355 Neg) — version-dependent; use "approx.".
- LM 3-word negation rule — secondary source only; verify against LM 2011 paper before teaching as fact.
- No verbatim company 10-K quote verified — use labelled paraphrases above until an EDGAR passage is pulled with accession no.
- FinBERT example probabilities are illustrative, not a model run.
- S10 "143,372" — confirmed slide error; needs MK's correction, not a research fix.
