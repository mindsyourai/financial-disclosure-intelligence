# Verification Report — Financial Disclosure Intelligence (ADAM) micro-learning site

**Site verified:** `~/workspace/projects/financial-disclosure-intelligence/index.html`
(160,642 bytes, built 2026-11-22 00:32; built by `build.py` from `modules/ep1-5.json`)
**Sources of truth:** `SLIDES_EXTRACT.txt` (20 ADAM slides + notes), `FACT_SHEET.md`
**Method:** cold, independent verification. Quiz questions solved from each episode's own
lesson text only (never from the keyed answer). Every number recomputed from source data.
Cold load driven over local HTTP with a from-scratch Node/vm harness
(`/tmp/fdi_verify.js`, 62 checks — written for this verification, not copied from
`smoke_test.js`). The builder's `validate.py` and `smoke_test.js` were run only as a
cross-check; both pass, but both miss the one real bug below because they only ever
play perfect first runs.
**Date:** 2026-11-22. **Verdict: CONDITIONAL FAIL — one real scoring bug + 3 minor
content nits. Everything else passes.**

## Headline counts

| Section | Result |
|---|---|
| 1. Quiz keys | **15/15 PASS** — every independently-derived answer matches the key and its explanation; every answer is taught in its own episode's lessons |
| 2. Derived numbers | **65/65 figures recomputed correctly** (LM 10/10, FinBERT 4/4, ADAM 51/51) |
| 3. Cold first load | **55/62 harness checks PASS; 7 FAIL — all 7 trace to ONE root cause** (perfect-run bonus, §3.1) |
| 4. Content checks | **PASS**, with 3 minor nits (§4.1–4.3) |
| XP totals | Formula 120 × 5 = 600 is correct as arithmetic, but **unreachable after any partial first clear** (see §3.1) |

---

## 1. Quiz keys — PASS 15/15

Solved each question independently from the lesson text of the same episode only.
For every question: my derived answer = keyed answer, and the explanation agrees
with both. No question's answer is untaught in its episode; no ambiguous question;
no explanation contradicts its key.

| Ep | Q | Question (short) | Independently derived answer | Key | Match |
|---|---|---|---|---|---|
| 1 | 1 | Which Item lists the most significant risks? | Item 1A — Risk Factors (L2) | Item 1A | ✓ |
| 1 | 2 | 55 firms, 2016–2025: firm-years + focal paragraphs? | 550; 179,623 (L3: 55×10, 94,031+85,592) | 550; 179,623 | ✓ |
| 1 | 3 | Why is negative Item 1A wording not itself bad news? | Tone/direction/informativeness differ; can be boilerplate (L3) | Boilerplate answer | ✓ |
| 2 | 1 | LM %Pos / %Neg in the 50-word example? | 5/50 = 10.0%; 6/50 = 12.0% (L2) | 10.0% / 12.0% | ✓ |
| 2 | 2 | LM 2011's own net-tone formula? | (Pos−Neg) ÷ total words = −0.02 (L2) | Total-words formula | ✓ |
| 2 | 3 | Why does a general dictionary misread 10-Ks? | ~73.8% of Harvard-IV negative counts are finance-neutral words (L1) | 73.8% answer | ✓ |
| 3 | 1 | FinBERT 0.62/0.30/0.08: class + confidence? | argmax Negative, confidence 0.62 (L2) | Negative, 0.62 | ✓ |
| 3 | 2 | What happens at confidence 0.62? | Below 0.80 → human review (L2) | Human review | ✓ |
| 3 | 3 | FinBERT's strength vs LM, and its limit? | Semantic context; lower traceability, no temporal/peer context (L1/L3) | Semantic-context answer | ✓ |
| 4 | 1 | ADAM best described as…? | Agentic: specialized agents + adjudicator, not a 3-vote ensemble (L1) | Agentic system | ✓ |
| 4 | 2 | What proves the architecture itself matters? | Info F1 0.453 → 0.469 → 0.607, Δ +.138/+.154 (L3) | Ablation answer | ✓ |
| 4 | 3 | FinBERT-negative rule for High informativeness? | 19.5% precision — proxy trap (L3) | 19.5% | ✓ |
| 5 | 1 | Why nested tests holding the adjudicator constant? | Separate architecture gain from LLM-alone gain (L3) | Architecture answer | ✓ |
| 5 | 2 | Which arm is paragraph + LM + FinBERT, no Context & Quality? | Base evidence (L3) | Base evidence | ✓ |
| 5 | 3 | Unanimous agreement only 21% for sentiment — conclusion? | Task genuinely difficult; disagreement is a signal, not only noise (L2) | Difficulty answer | ✓ |

Game keys also independently checked: Ep1 sort (Item 1A/MD&A, 4 items), Ep2 build
(5 / 6 / −0.02), Ep3 build (Negative / 0.62 / routes to review), Ep4 build
(loss+litigation / negation / conditional-negated-mixed), Ep5 sort
(Judge-only / Base / Full ADAM, 4 items) — all correct against their lessons.

---

## 2. Derived numbers — PASS 65/65

### 2a. LM worked example — 10/10
Re-counted the 50-word passage word by word from `FDI_WORDS` in the built page
(`index.html:1169`): the joined passage is byte-identical to the FACT_SHEET passage.
Total **50** words; Positive **5** (`Strong, improve, efficient, benefit, success`);
Negative **6** (`decline, loss, risk, volatility, weak, burden`); **%Pos = 5/50 = 10.0%**;
**%Neg = 6/50 = 12.0%**; net LM tone **(5−6)/50 = −0.02 (−2.0%)**;
per 1,000 words **Pos 100, Neg 120, net −20**. Henry tone **(5−6)/(5+6) = −1/11 = −0.091**.

Henry labelling: `−0.091` occurs 8×. Seven occurrences carry "Henry" (Henry's (2008))
within ±300 characters. The 8th is the bare distractor option "−0.02 and −0.091" in
Ep2 Q1 — it attributes the number to no one, and the question's explanation
explicitly labels it "Henry's (2008) tone measure — a different formula, not LM's".
No occurrence presents −0.091 as LM's. **Pass, with that one bare-option nit noted**
(see §4.3).

### 2b. FinBERT example — 4/4
**0.62 + 0.30 + 0.08 = 1.00** ✓; argmax = **Negative** ✓; confidence = max = **0.62** ✓;
0.62 < 0.80 → **routes to human review** ✓. Slider edge cases verified live in the
harness: 95/3/2 → Automated; exactly 80/10/10 → Automated (≥ 0.80);
79/11/10 → review; 10/10/80 → argmax Positive, Automated; 0/0/0 → normalized to
thirds, sum still displayed 1.00, review. Probabilities labelled "illustrative
teaching values, not a real model run" in Ep3 L2 and in the HQ "How to read the results" card.

### 2c. All ADAM numbers vs SLIDES_EXTRACT.txt — 51/51
Recomputed from the slide figures, not copied from the site:

- **179,623 = 94,031 + 85,592** ✓; **55 firms = 5 × 11 sectors** ✓; **55 × 10 yrs = 550 firm-years** ✓; historical context **32,407** (2014–2015) ✓
- **300 = 144 Item 1A + 156 Item 7** ✓
- Unanimous agreement **21% / 25% / 32%** ✓; agreement rows each sum to 100
  (21+66+13; 25+64+11; 32+54+14) ✓
- Sentiment accuracy **LM 37.3 / FinBERT 60.7 / Ensemble 58.7 / ADAM 82.7** ✓;
  macro-F1 **0.320 / 0.529 / 0.384 / 0.745** ✓
- Direction **83.3% / F1 0.689** ✓; informativeness **71.4% / F1 0.607** ✓
- Disagreement **162/300 = 54%** ✓; on disagreement **ADAM 76.5% / F1 0.703**,
  **FinBERT 68.5% / 0.606**, **LM 25.3%**, ensemble 64.8% ✓
- Both-wrong **77** paragraphs, ADAM correct **89.6%** (0.896 × 77 = 69.0; 69/77 = 89.6%) ✓
- Ablation info F1 **0.453 → 0.469 → 0.607**; deltas **0.607−0.469 = +0.138**,
  **0.607−0.453 = +0.154** ✓; full S17 table verified cell by cell
  (Judge-only 82.0/.731, 84.0/.683, 67.2/.453; Base 82.0/.730, 83.7/.694, 68.3/.469;
  Full ADAM 82.7/.745, 83.3/.689, 71.4/.607) — including the honest boundary the site
  states: Judge-only beats Full ADAM on direction (84.0% vs 83.3%) ✓
- Decision support: High-informativeness flag **81.0% precision / 69.9% recall** vs
  FinBERT-negative rule **19.5%** ✓
- Routing: **56%** to review (0.56 × 300 = 168); **92.3%** of errors captured
  (errors ≈ 300 × (1−0.827) ≈ 52; 92.3% ≈ 48); remainder 132 at **97.0%** (≈ 4 errors);
  48 + 4 = 52 ✓ (rounding-consistent, as in the fact sheet)
- LM list sizes are given as "approximate, version-dependent" (Pos ~354, Neg ~2,337–2,355,
  Unc ~297, Lit ~904, Strong Modal 19, Weak Modal 27, Constraining ~184 as a later
  2015 addition, not in the 2011 six) ✓. FinBERT PhraseBank size 4,845 ✓.
  The site omits FinBERT's 0.86/0.84 accuracy/F1 and PhraseBank split percentages —
  omission, not error; nothing invented was found in a full numeric sweep of the
  episode data (the only bare figures are rhetorical: a "99% certainty" tip in Ep5
  and "82%" rounded in an Ep5 game explanation, both accurate in context).

### 2d. XP / stars / levels
Formula correct: 3 lessons × 10 + 3 questions × 20 + 30 perfect bonus = **120/episode**;
**120 × 5 = 600**; `stars = state.score`; levels defined 0 Disclosure Rookie,
120 Paragraph Detective, 240 Tone Analyst, 360 Context Sleuth, 480 Adjudicator,
600 Disclosure Intelligence Master. **But see §3.1: 600 and the Master level are
unreachable after any partial first clear.**

### 2e. PRELIMINARY labelling + slide-10 error — PASS
Full banner **"PRELIMINARY — VALIDATION ONGOING"** occurs 6×, on every results
display: HQ "How to read the results" card, Ep4 L3 lesson text, and all three ADAM
visuals (`FDI_adamResults`, `FDI_adamDecision`, `FDI_adamAblation`). Ep3 L3 states
the 60.7% vs 37.3% comparison as "preliminary, validation ongoing"; Ep4 intro and
the footer repeat it. **"143,372" occurs 7× and every occurrence is the flagged slide
error** (Ep1 L3 body + pages, Ep1 Q2 option + explanation, Ep5 L2 body + pages, HQ
"A note on the numbers") — never presented as data. 179,623 is the figure used throughout.

---

## 3. Cold first load — 55/62 harness checks PASS; 7 FAIL (one root cause)

Cold load over local HTTP (200, bytes identical to disk). Two inline script blocks,
no `<script src>`, no remote images. Google Fonts link present, but every
`font-family` has a system fallback (`system-ui, sans-serif`, `monospace`), so the
page is usable offline. Certificate overlay markup precedes the script; all
interactive element IDs exist before the script runs. Scripts execute with no JS
error on cold load. Cold HUD: "0 / 5 cleared", "Level 1 · Disclosure Rookie".
Cold trail: only Episode 1 has a Play button; Episodes 2–5 render disabled Locked
buttons with no `data-play`. All 5 badges listed.

Verified working on cold first load: all 5 episode unlock chains (sequential,
in order); all 5 games (Ep1 item sorter, Ep2 LM build, Ep3 FinBERT build,
Ep4 adjudicator build, Ep5 evaluation-arm sorter) including wrong-pick hint path;
checkpoint answering with instant feedback (wrong answer shows the correct answer,
awards no XP); LM counter (50 chips, click-to-toggle with live recompute, Reveal →
5/6, −0.02, −20/1,000, "Exactly right", Reset → 0/0); FinBERT sliders (see §2b);
badges; certificate open (names the episode + badge), Close button, Escape and
backdrop handlers wired in source; replay keeps max stars and does not double-award
lesson/question XP.

### 3.1 FAIL — Perfect-run bonus is never awarded on a replay (the one real bug)

**Location:** `index.html:897–902` (`renderResults`).

```js
var firstClear = !state.cleared[state.current];
if (firstClear){
  state.cleared[state.current] = true;
  if (state.score === ep.quiz.length) awardXP("B" + state.current, XP_BONUS);
}
```

The +30 perfect-run bonus is awarded only when the episode is cleared for the
first time. `awardXP` (`index.html:821`) already guards against double-awarding
via `state.awarded[key]`, so the `firstClear` gate is unnecessary — and it makes
the bonus permanently unearnable for any episode first cleared imperfectly.

**Reproduced independently (fresh state, my harness — not the builder's):**
Ep1 answered 2/3 (Q1 wrong first) → stars 2, cleared, Ep2 unlocked, XP = 70
(30 lessons + 40 questions, no bonus) — correct. Replayed Ep1 perfectly (3/3) →
stars rise to 3, but XP goes 70 → **90, not 120**: only the missing question's
+20 is awarded; the +30 bonus is not. The results screen on that replay still
displays **"Perfect-run bonus +30 XP"** (`index.html:915`) even though +30 was
not awarded, and the certificate/results "Episode value: +120 XP"
(`index.html:917`, `:1140`) is then unreachable for that episode.

**Consequence:** after one partial first clear, the site total caps at **570/600**
and the top level "Disclosure Intelligence Master" (600 XP) is unreachable, even
with all 5 episodes at 3 stars. Harness failures caused by this single bug (7):
replay-bonus check (90 vs 120), cumulative XP after Ep2 (210 vs 240), Ep3 (330 vs
360), Ep4 (450 vs 480), Ep5 (570 vs 600), total-600 check, HUD Master-level check.
The builder's `smoke_test.js` never catches this because it only plays perfect
first runs.

**Suggested fix (builder):** move the bonus award out of the `if (firstClear)`
block so a later perfect replay awards it once via the existing `state.awarded`
guard, e.g. `if (state.score === ep.quiz.length) awardXP("B" + state.current, XP_BONUS);`
unconditionally in `renderResults`. Re-verify with a partial-then-perfect replay.

**Design observations (not fails):** an episode counts as cleared — and unlocks the
next — even with a 0/3 checkpoint (verdict text honestly says "deserves a rematch");
`openEpisode` itself has no unlock guard, but locked episodes expose no Play button,
so the chain is enforced in the UI. Both match the sibling QM/MBA engine's behaviour.

---

## 4. Content checks — PASS, with 3 minor nits

- **Authors credited:** Kazim Topuz (presenter), Jessica Bedson, Tally Ferguson,
  Thomas Kim, University of Tulsa, DSI 2026 — in Ep4 L1, HQ "The ADAM authors",
  footer, certificate signature (Dr. Kazim Topuz). Contact Kazim-Topuz@utulsa.edu ✓
- **Sources present:** Loughran & McDonald (2011) *Journal of Finance* 66(1), 35–65;
  Araci (2019) arXiv:1908.10063 (correctly noted as preprint/MSc thesis, not
  peer-reviewed); Bochkay, Brown, Leone & Tucker (2023) *Contemporary Accounting
  Research* 40(2), 765–805; Brown & Tucker (2011) *Journal of Accounting Research*
  49(2), 309–348; Hevner, March, Park & Ram (2004) *MIS Quarterly* 28(1), 75–105;
  plus SEC "How to Read a 10-K/10-Q" — all in the HQ Sources card with one-line
  descriptions matching the fact sheet ✓
- **No invented numbers; no verbatim company 10-K quotes presented as real.**
  All 10-K passages are labelled "illustrative paraphrase, not a company quote" /
  "written in the style of a 10-K"; the disagreement passage is labelled
  "illustrative passage"; FinBERT probabilities are labelled illustrative (§2b) ✓
- **Session-only progress noted** in HQ ("all progress … lives in memory for this
  session only and resets when the page reloads"), footer, and certificate
  ("Practice companion — progress is session-only") ✓

### 4.1 Nit — Episode 4 intro calls itself the "Final episode"
Ep4 intro (in the `EPISODES` data, `index.html:704`): *"Final episode, and Dr. K
saved the real idea for last."* Episode 4 is not final — Episode 5 follows and
its intro says *"this last episode is about the study itself"*. One of the two
intros is wrong; Ep4's should say something like "the real idea" without "Final".

### 4.2 Nit — Stale template placeholder in the hidden certificate overlay
`index.html:688`: `<div class="c-badge" id="cert-badge">Framing Badge</div>` —
"Framing Badge" is a leftover from the QM 7073 template (no such badge exists here).
It is overwritten by `openCert` whenever the certificate opens, so it is not
user-visible in normal flow, but the static file still carries the wrong badge name.

### 4.3 Nit — Bare −0.091 in one quiz distractor option
Ep2 Q1 option 4 is "−0.02 and −0.091" with no Henry label inside the option text.
The explanation correctly attributes −0.091 to Henry (2008). Low risk, but for
strict "labelled Henry everywhere it appears", the option could read
"−0.02 and −0.091 (Henry)".

---

## Summary for the builder

1. **Fix (blocking):** perfect-run bonus gated on `firstClear` (`index.html:897–902`) —
   a partial first clear permanently loses the +30 bonus, caps the site at 570/600,
   and the results screen still claims "+30 XP" on a replayed perfect run.
   Move the bonus award out of the `firstClear` block; `awardXP` already dedupes.
2. **Fix (trivial):** Ep4 intro "Final episode" → reword (§4.1).
3. **Fix (trivial):** certificate placeholder "Framing Badge" → a neutral default (§4.2).
4. **Optional:** label −0.091 as Henry's inside the Ep2 Q1 distractor option (§4.3).

Everything else verified — quiz 15/15, derived numbers 65/65, cold-load
interactives 55/62 (7 fails all from bug #1), credits/sources/session-only/
illustrative labelling all correct. Re-verify after the fix with a partial-then-perfect
replay (the case the builder's own smoke test does not cover).

---

# RE-VERIFICATION — 2026-11-22 (after the fix)

**File verified:** `index.html`, 159,735 bytes, sha256 `300913a0499307a846ae94e9c8ec50951a73530b9e8d6919f458d3c102dfa16d`,
built 2026-11-22 00:37. **Method:** cold, independent re-verification. Two fresh
harnesses written from scratch for this round (`/tmp/fdi_reverify.js`, 41 checks;
`/tmp/fdi_reverify2.js`, 20 checks) driving the built page in jsdom **only through
DOM clicks/inputs** (trail Play buttons, Next, quiz options, game buttons,
word chips, sliders). The builder's `validate.py`/`smoke_test.js` were not used as
evidence. Quiz questions were re-solved independently from each episode's own
lesson text (never from the key). Every derived number was recomputed from
`SLIDES_EXTRACT.txt` / `FACT_SHEET.md` / the page's own `FDI_WORDS` data.
**Verdict: PASS — the blocking bug is fixed, all 3 nits are fixed, no regressions found.**

## 1. The blocking bug — PASS (fixed)

Fix confirmed in source first, then proven live. `renderResults` now awards the
bonus outside the `firstClear` block, gated only on a 3/3 score and the existing
`state.awarded` dedupe, and the results line shows "Perfect-run bonus +30 XP"
only when `bonusAwarded` is true on that run (i.e. the claim and the award can no
longer diverge).

**Observed XP sequence, Episode 1, fresh load (harness 1, TEST 1):**

| Step | Checkpoint | XP observed | Stars | "Perfect-run bonus +30 XP" shown? |
|---|---|---|---|---|
| First clear, Q1 wrong | 2/3 | **70** (30 lessons + 40 questions) | 2 | No |
| Replay, all correct | 3/3 | **120** (+20 missing question +30 bonus) | 3 | Yes |
| Replay again, all correct | 3/3 | **120** (unchanged — no second +30) | 3 | No |

Then Episodes 2–5 played perfect first runs in the same session:
240 → 360 → 480 → **600**, HUD level **"Level 6 · Disclosure Intelligence Master"**.
The 600 XP total and top level are now reachable after a partial first clear —
the exact case that previously capped at 570.

Control case (fresh load, TEST 2): perfect first run of Ep1 gives **120 XP, 3 stars,
bonus shown** — unchanged behaviour for the already-working path. No JS errors in
any run (jsdom's missing `scrollTo`/`matchMedia` were stubbed in the harness, as
real browsers provide both; with stubs, zero errors across all three test loads).

## 2. The 3 nits — PASS (all fixed)

- **(a) Ep4 intro:** "Final episode" occurs **0×** in the built file. Ep4 intro now
  reads *"Dr. K saved the real idea for last — well, almost last: one episode
  follows this one, and it is about the study itself."* Ep5 still coherently calls
  itself the last episode: *"this last episode is about the study itself"*.
- **(b) "Framing Badge":** occurs **0×** anywhere in the built `index.html`,
  including the hidden certificate overlay. The placeholder is now
  `<div class="c-badge" id="cert-badge">Episode Badge</div>`. Note for the record:
  the string still appears 3× in `build.py` itself — as the search string of the
  fix's own replace rule, its comment, and the generator's forbidden-string
  assertion that the final output must NOT contain it. That is the fix machinery,
  not a leftover in the site.
- **(c) Ep2 Q1 distractor:** option D now reads **"−0.02 and −0.091 (Henry's measure)"**,
  in both `modules/ep2.json` and the built file. Correct answer unchanged (A,
  10.0% and 12.0%). Every other −0.091 occurrence was already labelled Henry's;
  the bare option was the only unlabelled one and is now labelled.

## 3. Regression spot-checks — PASS

- **Quiz keys 15/15** — every question re-solved independently from its own
  episode's lesson text; derived answer = keyed answer in all 15, explanations
  agree. (Ep1: 1A / 550 + 179,623 / boilerplate; Ep2: 10.0%/12.0% / total-words
  formula / 73.8%; Ep3: Negative 0.62 / human review / semantic context + low
  traceability; Ep4: agentic system / ablation Δ +.138/+.154 / 19.5%;
  Ep5: architecture-vs-LLM separation / Base evidence / genuine difficulty.)
  Game keys also re-checked against lesson text: Ep1 sort (Item 1A/MD&A),
  Ep2 build (5 / 6 / −0.02), Ep3 build (Negative / 0.62 / review), Ep4 build
  (loss+litigation / negation / conditional-negated-mixed), Ep5 sort
  (Judge-only / Base / Full ADAM) — all correct.
- **LM worked example — re-counted from `FDI_WORDS` in the built page:**
  50 `[word, tag]` pairs; Positive **5** (Strong, improve, efficient, benefit,
  success); Negative **6** (decline, loss, risk, volatility, weak, burden);
  %Pos **10.0%**, %Neg **12.0%**, net **(5−6)/50 = −0.02**, per 1,000 words
  **100 / 120 / −20**; Henry **(5−6)/(5+6) = −0.091**. All match the site.
- **FinBERT example — re-checked live:** default sliders 0.62/0.30/0.08 sum to
  **1.00**, argmax **Negative**, confidence **0.62**, routes to review (0.62 < 0.80).
  Slider edges driven live: 95/3/2 → Automated, conf 0.95; exactly 80/10/10 →
  Automated (boundary ≥ 0.80); 79/11/10 → review; 10/10/80 → argmax Positive,
  Automated. **LM counter driven live:** 50 word chips; Reveal → 5/6, −0.02,
  −20/1,000, "Exactly right"; Reset → 0/0; toggling "Strong" + "decline" →
  1 pos / 1 neg, 2.0% / 2.0%, net 0.00.
- **ADAM numbers — 24 figures spot-checked against `SLIDES_EXTRACT.txt`**
  (well over the 10 required): 179,623 = 94,031 + 85,592; 55 × 10 = 550;
  300 = 144 + 156; agreement rows sum to 100 (21+66+13; 25+64+11; 32+54+14);
  sentiment 37.3 / 60.7 / 58.7 / 82.7, macro-F1 0.320 / 0.529 / 0.384 / 0.745;
  direction 83.3% / F1 0.689; informativeness 71.4% / F1 0.607; ablation
  0.453 → 0.469 → 0.607, deltas +0.138 / +0.154; disagreement 162/300 = 54%,
  ADAM 76.5% / 0.703, FinBERT 68.5% / 0.606, LM 25.3%, ensemble 64.8%;
  both-wrong 77, ADAM correct 89.6%; decision support 81.0% / 69.9% vs
  FinBERT-negative 19.5%; routing 56% to review, 92.3% of errors captured,
  97.0% on the automated remainder. All present in the built file and matching
  the slides.
- **Cold first load — all 5 episodes:** fresh load shows only Ep1 playable
  (Ep2–5 disabled Locked); each episode unlocks the next in order; all 5 games
  complete on first load (Ep1 sort, Ep2 build, Ep3 build, Ep4 build, Ep5 sort);
  certificate opens (overlay `open`) and closes without error; zero JS errors.
  Harness totals: **41/41** (harness 1) and **20/20** (harness 2).

## 4. Build reproducibility — PASS

`build.py` re-run in a scratch copy (`/tmp/fdi_regen`) regenerates
`index.html` **byte-identical** to the verified file (same sha256
`300913a0…`). The fix lives in the generator (bonus award + bonus display
+ cert placeholder + forbidden-string assertion), not as a hand-edit to the
built file, so it survives regeneration.

## Re-verification summary

| Item | Result |
|---|---|
| 1. Scoring bug (partial → replay → replay) | **PASS** — XP 70 → 120 → 120; bonus shown only when awarded; 600 + Master level reachable |
| 2a. Ep4 "Final episode" | **PASS** — 0×; Ep5 still the last episode |
| 2b. "Framing Badge" | **PASS** — 0× in built file (placeholder now "Episode Badge") |
| 2c. Ep2 Q1 Henry label | **PASS** — "−0.02 and −0.091 (Henry's measure)"; key unchanged |
| 3. Quiz keys | **PASS 15/15** |
| 3. LM / FinBERT numbers + live interactives | **PASS** — recount + slider/counter edges all correct |
| 3. ADAM numbers spot-check | **PASS 24/24** vs slides |
| 3. Cold first load, all 5 games | **PASS 41/41 + 20/20 harness checks, 0 JS errors** |
| 4. Regeneration | **PASS — byte-identical** |

**Overall: PASS.** No remaining failures. The one caveat from round 1 that still
stands is scope, not a defect: verification was in jsdom (a real-browser DOM),
not a live browser — the page has no remote dependencies other than a Google
Fonts link with system fallbacks, and nothing in the harness results depends on
that link. A live-browser smoke pass remains optional, not required, for this fix.
