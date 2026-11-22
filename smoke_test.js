/* Headless smoke test for the built FDI index.html.
   Minimal DOM shim; drives the real engine: all 5 episodes end-to-end
   (lessons, games, checkpoints, unlock chain) + the FDI interactives.
   Run: node smoke_test.js  (from this folder; no dependencies, no network) */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (scripts.length !== 2) throw new Error("expected 2 script blocks, got " + scripts.length);

function makeClassList() {
  const s = new Set();
  return { add(c) { s.add(c); }, remove(c) { s.delete(c); },
    contains(c) { return s.has(c); },
    toggle(c) { s.has(c) ? s.delete(c) : s.add(c); }, _s: s };
}
function parseButtons(html, sel) {
  const out = [];
  const re = /<button([^>]*)>/g;
  let m;
  while ((m = re.exec(html))) {
    const attrs = m[1];
    const cls = /class="([^"]*)"/.exec(attrs);
    const classes = cls ? cls[1].split(/\s+/) : [];
    let want = false;
    if (sel === ".opt" && classes.includes("opt")) want = true;
    if (sel === ".gbtn" && classes.includes("gbtn")) want = true;
    if (sel === ".lmw" && classes.includes("lmw")) want = true;
    if (sel === "[data-play]" && /data-play="/.test(attrs)) want = true;
    if (!want) continue;
    const el = makeEl("anon");
    const getA = (k) => { const r = new RegExp(k + '="([^"]*)"').exec(attrs); return r ? r[1] : null; };
    el._attrs["data-oi"] = getA("data-oi");
    el._attrs["data-ii"] = getA("data-ii");
    el._attrs["data-bi"] = getA("data-bi");
    el._attrs["data-gi"] = getA("data-gi");
    el._attrs["data-play"] = getA("data-play");
    el._attrs["data-cls"] = getA("data-cls");
    out.push(el);
  }
  return out;
}
const qcache = new Map();
function queryFromHTML(html, sel) {
  const key = sel + "::" + html;
  if (!qcache.has(key)) qcache.set(key, parseButtons(html, sel));
  return qcache.get(key);
}
function makeEl(id) {
  const el = {
    id: id || "", _html: "", textContent: "", value: "", disabled: false,
    style: {}, _attrs: {}, _handlers: {},
    classList: makeClassList(),
    addEventListener(ev, fn) { (this._handlers[ev] = this._handlers[ev] || []).push(fn); },
    getAttribute(k) { return this._attrs[k] !== undefined ? this._attrs[k] : null; },
    setAttribute(k, v) { this._attrs[k] = String(v); },
    focus() {},
    click() { const h = this._handlers.click || []; h.forEach((f) => f.call(this)); },
    querySelectorAll(sel) { return queryFromHTML(this._html, sel); },
  };
  Object.defineProperty(el, "innerHTML", {
    get() { return el._html; }, set(v) { el._html = String(v); },
  });
  return el;
}
const registry = {};
const document = {
  getElementById(id) { if (!registry[id]) registry[id] = makeEl(id); return registry[id]; },
  querySelectorAll(sel) {
    if (sel === "[data-play]") return queryFromHTML(registry.trail ? registry.trail._html : "", sel);
    if (sel === ".opt") return queryFromHTML(registry["p-stage"] ? registry["p-stage"]._html : "", sel);
    if (sel === "#p-stage .lmw") return queryFromHTML(registry["p-stage"] ? registry["p-stage"]._html : "", ".lmw");
    return [];
  },
  addEventListener() {},
};
const sandbox = {
  document, console,
  window: null,
  matchMedia: () => ({ matches: false }),
  scrollTo() {}, print() {},
  setTimeout: () => 0, clearTimeout() {},
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(scripts[0], sandbox);
vm.runInContext(scripts[1], sandbox);
const assert = (c, msg) => { if (!c) throw new Error("FAIL: " + msg); };

function lastClick(id) {
  const el = document.getElementById(id);
  const h = el._handlers.click || [];
  assert(h.length > 0, "no click handler on #" + id);
  h[h.length - 1].call(el);
}
function clickOpt(oi) {
  const opts = document.querySelectorAll(".opt");
  const b = opts.find((o) => o.getAttribute("data-oi") === String(oi));
  assert(b, "opt " + oi + " not found");
  b.click();
}
function completeGame(ep) {
  const g = ep.lessons[2].game;
  const box = document.getElementById("game-box");
  if (g.type === "sort") {
    const btns = box.querySelectorAll(".gbtn");
    g.items.forEach((it, ii) => {
      const b = btns.find((x) => x.getAttribute("data-ii") === String(ii) && x.getAttribute("data-bi") === String(it.b));
      assert(b, "sort button missing ep" + ep.n + " item " + ii);
      b.click();
    });
  } else {
    const btns = box.querySelectorAll(".gbtn");
    g.groups.forEach((gr, gi) => {
      const b = btns.find((x) => x.getAttribute("data-gi") === String(gi) && x.getAttribute("data-oi") === String(gr.a));
      assert(b, "build button missing ep" + ep.n + " group " + gi);
      b.click();
    });
    lastClick("gcheck");
  }
  assert(sandbox.state.gamesDone["G" + (ep.n - 1) + "-2"], "game not marked done, ep " + ep.n);
}
function playEpisode(n) {
  const ep = sandbox.EPISODES[n];
  // Fresh DOM nodes per episode, like a real browser render: drop the
  // per-game stubs (gi-/gw-/gg-/gh-/gdone/game-box/gcheck) whose classList
  // would otherwise leak "ok" from an earlier episode's game.
  Object.keys(registry).forEach((k) => {
    if (/^(gi-|gw-|gg-|gh-|gdone|game-box|gcheck)/.test(k)) delete registry[k];
  });
  sandbox.openEpisode(n);
  let guard = 0;
  while (sandbox.state.step < ep.lessons.length) {
    if (++guard > 60) throw new Error("lesson loop stuck, ep " + ep.n);
    const stage = document.getElementById("p-stage")._html;
    if (stage.includes('id="game-box"')) completeGame(ep);
    lastClick("btn-next");
  }
  for (let qi = 0; qi < ep.quiz.length; qi++) {
    clickOpt(ep.quiz[qi].a);
    lastClick("btn-qnext");
  }
  assert(sandbox.state.cleared[n] === true, "ep " + ep.n + " not cleared");
  assert(sandbox.state.stars[n] === 3, "ep " + ep.n + " stars != 3");
  assert(sandbox.state.xp === (n + 1) * 120, "xp after ep " + ep.n + " = " + sandbox.state.xp);
  if (n < 4) assert(sandbox.isUnlocked(n + 1), "ep " + (n + 2) + " not unlocked");
  console.log(`episode ${ep.n} "${ep.title}" cleared: 3 stars, ${sandbox.state.xp} XP total`);
}

// cold load
assert(document.getElementById("trail")._html.includes("10-K Navigator Badge"), "trail missing ep1 badge");
assert(document.getElementById("trail")._html.includes("Design Scientist Badge"), "trail missing ep5 badge");
assert(document.getElementById("hud-cleared").textContent === "0 / 5 cleared", "hud cleared text");
for (let n = 0; n < 5; n++) playEpisode(n);
assert(sandbox.state.xp === 600, "total XP != 600");
console.log("ENGINE: all 5 episodes played end-to-end, 600 XP, sequential unlocking OK");

// FDI interactives
const lmHtml = sandbox.FDI_lmCounter();
assert((lmHtml.match(/class="lmw"/g) || []).length === 50, "LM counter must render 50 chips");
document.getElementById("p-stage").innerHTML = lmHtml;
sandbox.FDI_lmReveal();
sandbox.FDI_lmScore();
const lmScore = document.getElementById("fdi-lm-score").innerHTML;
assert(lmScore.includes("Positive: <b>5</b>") && lmScore.includes("Negative: <b>6</b>"), "LM score 5/6: " + lmScore);
assert(lmScore.includes("Net LM tone: <b>-0.02</b>") && lmScore.includes("<b>-20</b>"), "LM net tone: " + lmScore);
assert(document.getElementById("fdi-lm-note").textContent.includes("Exactly right"), "LM note");
console.log("LM COUNTER: reveal -> 5 positive, 6 negative, net -0.02, -20 per 1,000 OK");

const fbHtml = sandbox.FDI_finbertBar();
assert(fbHtml.includes("0.62") && fbHtml.includes("Routes to human review"), "FinBERT bar initial state");
document.getElementById("fdi-fb-n").value = "62";
document.getElementById("fdi-fb-u").value = "30";
document.getElementById("fdi-fb-p").value = "8";
sandbox.FDI_fbUpdate();
let v = document.getElementById("fdi-fb-verdict");
assert(v.textContent.includes("Routes to human review"), "0.62 must route to review: " + v.textContent);
assert(document.getElementById("fdi-fb-score").innerHTML.includes("Negative"), "argmax Negative");
document.getElementById("fdi-fb-n").value = "95";
document.getElementById("fdi-fb-u").value = "3";
document.getElementById("fdi-fb-p").value = "2";
sandbox.FDI_fbUpdate();
v = document.getElementById("fdi-fb-verdict");
assert(v.textContent.includes("Automated"), "0.95 must automate: " + v.textContent);
console.log("FINBERT BAR: 0.62 routes to review, 0.95 automates OK");

assert(sandbox.FDI_adamData().includes("179,623"), "adam-data");
assert(sandbox.FDI_adamResults().includes("82.7%") && sandbox.FDI_adamResults().includes("PRELIMINARY"), "adam-results");
assert(sandbox.FDI_adamDecision().includes("89.6%") && sandbox.FDI_adamDecision().includes("76.5%"), "adam-decision");
assert(sandbox.FDI_adamAblation().includes("+.138") && sandbox.FDI_adamAblation().includes("+.154"), "adam-ablation");
console.log("ADAM VISUALS: data/results/decision/ablation OK");
console.log("HEADLESS SMOKE TEST: ALL PASSED");
