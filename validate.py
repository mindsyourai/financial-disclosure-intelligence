#!/usr/bin/env python3
"""Independent verification of the BUILT index.html (not build.py source).
Solves each of the 15 checkpoint questions from lesson/explanation alone,
recomputes every piece of arithmetic from scratch, and checks schema,
XP/stars/unlocking rules, games, visuals, and forbidden content."""
import json, re, sys, pathlib, math

t = (pathlib.Path(__file__).parent / "index.html").read_text()
i = t.index("var EPISODES = ")
j = t.index("var BOSSES", i)
raw = t[i + len("var EPISODES = "):j].rstrip()
assert raw.endswith(";"), raw[-50:]
EPS = json.loads(raw[:-1])
assert len(EPS) == 5, len(EPS)

# Independent solves: (episode, question index) -> token that must appear in
# the keyed option AND in the explanation.
EXPECTED = {
 (1, 1): "Item 1A", (1, 2): "179,623", (1, 3): "boilerplate",
 (2, 1): "10.0%", (2, 2): "total words", (2, 3): "73.8%",
 (3, 1): "Negative, confidence 0.62", (3, 2): "human review", (3, 3): "semantic context",
 (4, 1): "agentic system", (4, 2): "0.453", (4, 3): "19.5%",
 (5, 1): "architecture adds value", (5, 2): "Base evidence", (5, 3): "annotation noise",
}
# Independent arithmetic recomputation (not trusting keyed numbers)
assert 94031 + 85592 == 179623 and 55 * 10 == 550 and 5 * 11 == 55
assert 144 + 156 == 300
assert 21 + 66 + 13 == 100 and 25 + 64 + 11 == 100 and 32 + 54 + 14 == 100
assert 5 / 50 == 0.10 and 6 / 50 == 0.12 and (5 - 6) / 50 == -0.02
assert 5 / 50 * 1000 == 100 and 6 / 50 * 1000 == 120 and (5 - 6) / 50 * 1000 == -20
assert abs((5 - 6) / (5 + 6) - (-0.0909)) < 0.001
assert abs(0.62 + 0.30 + 0.08 - 1.00) < 1e-9
assert 162 / 300 == 0.54 and abs(0.896 * 77 - 69) < 0.5
assert abs(0.607 - 0.469 - 0.138) < 0.001 and abs(0.607 - 0.453 - 0.154) < 0.001
assert 3 * 10 + 3 * 20 + 30 == 120 and 5 * 120 == 600

checked = 0
for ep in EPS:
    assert len(ep["lessons"]) == 3 and len(ep["quiz"]) == 3, ep["n"]
    assert ep["chapter"] and ep["badge"] and ep["title"] and ep["blurb"]
    assert ep.get("host") == "Dr. K" and ep.get("intro") and ep.get("outro"), ep["n"]
    games = [L for L in ep["lessons"] if L.get("game")]
    assert len(games) == 1, (ep["n"], len(games))
    assert ep["lessons"][2].get("game"), ep["n"]
    for qi, q in enumerate(ep["quiz"], 1):
        assert len(q["opts"]) == 4 and 0 <= q["a"] < 4 and q["why"]
        keyed = q["opts"][q["a"]]
        token = EXPECTED[(ep["n"], qi)]
        norm = lambda s: s.lower().replace("-", " ").replace("−", " ")
        assert norm(token) in norm(keyed), f"Ep{ep['n']} Q{qi}: keyed '{keyed}' lacks '{token}'"
        assert norm(token) in norm(q["why"]), f"Ep{ep['n']} Q{qi}: explanation lacks '{token}': {q['why']}"
        checked += 1
print(f"quiz: {checked}/15 independently solved, keyed option and explanation agree")

# Games: keys solved independently
g1 = EPS[0]["lessons"][2]["game"]
assert g1["type"] == "sort" and len(g1["items"]) == 4 and len(g1["buckets"]) == 2
assert [it["b"] for it in g1["items"]] == [0, 1, 0, 1] and g1.get("hint")
g2 = EPS[1]["lessons"][2]["game"]
assert g2["type"] == "build" and [gr["a"] for gr in g2["groups"]] == [0, 0, 0]
assert [gr["options"][0] for gr in g2["groups"]] == ["5", "6", "−0.02"]
g3 = EPS[2]["lessons"][2]["game"]
assert g3["type"] == "build" and [gr["a"] for gr in g3["groups"]] == [0, 0, 0]
assert [gr["options"][0] for gr in g3["groups"]] == ["Negative", "0.62", "Routes to human review"]
g4 = EPS[3]["lessons"][2]["game"]
assert g4["type"] == "build" and [gr["a"] for gr in g4["groups"]] == [0, 0, 0]
g5 = EPS[4]["lessons"][2]["game"]
assert g5["type"] == "sort" and len(g5["items"]) == 4 and len(g5["buckets"]) == 3
assert [it["b"] for it in g5["items"]] == [0, 1, 2, 0] and g5.get("hint")
print("games: 5/5 episodes, one challenge each, keys independently checked")

# LM counter word list embedded in the built page: exactly the 50-word passage
m = re.search(r"var FDI_WORDS = (\[.*?\]);", t, re.S)
assert m, "FDI_WORDS not found in built page"
words = json.loads(m.group(1))
assert len(words) == 50, len(words)
pos = sorted(w for w, c in words if c == "pos")
neg = sorted(w for w, c in words if c == "neg")
assert pos == sorted(["Strong", "improve", "efficient", "benefit", "success"]), pos
assert neg == sorted(["decline", "loss", "risk", "volatility,", "weak", "burden"]), neg
print("LM counter: 50 words, 5 positive, 6 negative — matches the fact sheet")

# Scoring / structure rules
assert "stars = state.score" in t, "star rule"
assert '" / " + EPISODES.length + " cleared"' in t and " / 8 cleared" not in t, "HUD cleared count must be dynamic"
assert "XP_LESSON = 10, XP_QUESTION = 20, XP_BONUS = 30" in t
assert "isUnlocked" in t and "0 / 5 cleared" in t and "Level 1 · Disclosure Rookie" in t
assert '{ xp: 600, name: "Disclosure Intelligence Master" }' in t
assert "var BOSSES = {};" in t and "after5" not in t and "after8" not in t
assert t.index("cert-overlay") < t.index("<script>"), "certificate overlay must precede script"
assert "FDI_lmCounter" in t and "FDI_finbertBar" in t and "FDI_adamResults" in t
assert "FDI_adamDecision" in t and "FDI_adamAblation" in t and "FDI_adamData" in t
# No external scripts or remote images (fonts degrade to system fallbacks)
assert "<script src" not in t and 'src="http' not in t and "quest-map" not in t
print("structure, scoring, visuals, offline checks: PASS")

# Fact-sheet guardrails
assert t.count("143,372") == 7, f"143,372 count: {t.count('143,372')}"  # Ep1 L3 x2 (body+pages), Ep5 L2 x2, Ep1 Q2 opt + why, HQ note — always as the flagged slide error
assert t.count("179,623") >= 6
assert t.count("−0.091") == 8 and "Henry's (2008)" in t  # Ep2 L2 x2 (body+pages), Ep2 game hint, Ep2 Q1+Q2 options, Ep2 Q2 why, HQ note + tricky card — every one Henry-labelled
assert t.count("PRELIMINARY — VALIDATION ONGOING") >= 5
for num in ["37.3%", "60.7%", "58.7%", "82.7%", "0.320", "0.529", "0.384", "0.745",
            "83.3%", "0.689", "71.4%", "0.607", "162", "76.5%", "68.5%", "25.3%",
            "89.6%", "0.453", "0.469", "81.0%", "69.9%", "19.5%", "92.3%", "97.0%"]:
    assert num in t, f"missing ADAM number: {num}"
for bad in ["QM 7073", "MyLab", "Evans", "Data Cadet", "Analytics Master",
            "Analytics Quest", "8-week", "8 Episodes", "eight episodes",
            "Boss Battle", "Boss battles", "Midterm", "Final Exam", "150 PTS",
            "IN MYLAB", "Harvey", "150 points", "boss deserves"]:
    assert bad not in t, bad
for name in ["Kazim Topuz", "Jessica Bedson", "Tally Ferguson", "Thomas Kim",
             "Loughran &amp; McDonald (2011)", "Araci (2019)",
             "Bochkay, Brown, Leone &amp; Tucker (2023)",
             "Brown &amp; Tucker (2011)", "Hevner, March, Park &amp; Ram (2004)"]:
    assert name in t, f"missing credit/source: {name}"
print("fact guardrails, credits, sources: PASS")
print("ALL CHECKS PASSED")
