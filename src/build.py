#!/usr/bin/env python3
"""Builds the Valugent site from the pieces in src/: one shared look, one page per topic, and the files search
engines read. Run from the repository root: python3 src/build.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SITE = "https://valugent.ai"
EMAIL = "hello@valugent.ai"
UPDATED = "2026-11-27"

CSS = (SRC / "base.css").read_text() + """
.status { display: flex; gap: 22px; }
.page .bar { position: relative; }
.crumbs { font-family: var(--display); font-stretch: 110%; text-transform: uppercase; letter-spacing: 0.2em;
  font-size: 12px; color: var(--dim); }
.crumbs a { color: var(--dim); text-decoration: none; }
.crumbs a:hover, .crumbs a:focus-visible { color: var(--ink); }
.page-head { padding: clamp(40px, 7vw, 96px) clamp(16px, 5vw, 64px) clamp(40px, 6vw, 72px); display: grid; gap: 24px;
  max-width: 1200px; }
.page-head h1 { font-size: clamp(36px, 6vw, 92px); }
.prose { padding: 0 clamp(16px, 5vw, 64px) clamp(64px, 9vw, 120px); display: grid; gap: clamp(40px, 5vw, 64px); }
.prose section { display: grid; grid-template-columns: minmax(0, 4fr) minmax(0, 8fr); gap: clamp(20px, 4vw, 64px);
  border-top: 1px solid var(--line); padding-top: clamp(28px, 4vw, 48px); }
.prose h2 { font-family: var(--display); font-weight: 800; font-stretch: 120%; text-transform: uppercase;
  font-size: clamp(22px, 2.4vw, 32px); line-height: 1.05; letter-spacing: 0.02em; text-wrap: balance; }
.prose h2 span { display: block; font-size: 12px; letter-spacing: 0.24em; color: var(--glow); margin-bottom: 12px;
  font-weight: 600; font-variant-numeric: tabular-nums; }
.prose .body { display: grid; gap: 16px; max-width: 40em; color: var(--dim); font-size: clamp(17px, 1.3vw, 19px); }
.prose .body p:first-child { color: var(--ink); }
.prose .body ul { margin: 0; padding-left: 1.2em; display: grid; gap: 8px; }
.faq { padding: clamp(64px, 9vw, 120px) clamp(16px, 5vw, 64px); border-top: 1px solid var(--line); }
.faq h2 { font-family: var(--display); font-weight: 900; font-stretch: 125%; text-transform: uppercase; line-height: 0.98;
  font-size: clamp(30px, 4.2vw, 60px); margin-top: 16px; text-wrap: balance; }
.faq dl { margin: clamp(32px, 4vw, 56px) 0 0; display: grid; gap: 0; border-top: 1px solid var(--line); }
.faq .qa { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: clamp(16px, 4vw, 64px);
  padding: 28px 0; border-bottom: 1px solid var(--line); }
.faq dt { font-family: var(--display); font-weight: 700; font-stretch: 115%; font-size: clamp(18px, 1.6vw, 22px);
  line-height: 1.25; }
.faq dd { margin: 0; color: var(--dim); max-width: 40em; }
.more { display: inline-block; margin-top: 28px; font-family: var(--display); font-stretch: 115%; text-transform: uppercase;
  letter-spacing: 0.18em; font-size: 13px; color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--glow);
  padding-bottom: 4px; }
.more:hover, .more:focus-visible { color: var(--glow); }
.cta { display: flex; flex-wrap: wrap; align-items: center; gap: 14px 24px; }
.cta span { color: var(--dim); font-size: 15px; max-width: 26em; }
.btn { display: inline-block; font-family: var(--display); font-weight: 700; font-stretch: 115%; text-transform: uppercase;
  letter-spacing: 0.16em; font-size: 13px; color: #05070b; background: var(--ink); text-decoration: none;
  padding: 15px 26px; border-radius: 2px; transition: background 0.2s, box-shadow 0.2s; }
.btn:hover, .btn:focus-visible { background: var(--glow); box-shadow: 0 0 28px rgba(156,196,255,0.35); }
.next { padding: clamp(48px, 7vw, 96px) clamp(16px, 5vw, 64px); border-top: 1px solid var(--line); background: var(--deep);
  display: flex; flex-wrap: wrap; gap: 16px 48px; align-items: baseline; justify-content: space-between; }
.next p { font-family: var(--display); font-weight: 800; font-stretch: 120%; text-transform: uppercase;
  font-size: clamp(22px, 2.6vw, 36px); line-height: 1.05; max-width: 22em; }
/* the cursor: a small node of light with a ring that follows it (mouse and trackpad only) */
.cur-dot, .cur-ring { position: fixed; left: 0; top: 0; pointer-events: none; z-index: 9999; border-radius: 50%;
  opacity: 0; transition: opacity 0.2s; will-change: transform; }
.cur-dot { width: 6px; height: 6px; margin: -3px 0 0 -3px; background: #eef1f5;
  box-shadow: 0 0 10px 2px rgba(156, 196, 255, 0.9); }
.cur-ring { width: 24px; height: 24px; margin: -12px 0 0 -12px; border: 1px solid rgba(156, 196, 255, 0.55);
  transition: opacity 0.2s, width 0.25s, height 0.25s, margin 0.25s, border-color 0.25s, background 0.25s; }
.has-cursor .cur-dot, .has-cursor .cur-ring { opacity: 1; }
.has-cursor, .has-cursor * , .has-cursor .hero { cursor: none !important; }
.cur-ring.link { width: 38px; height: 38px; margin: -19px 0 0 -19px; background: rgba(156, 196, 255, 0.08);
  border-color: rgba(156, 196, 255, 0.9); }
.cur-ring.brain { width: 44px; height: 44px; margin: -22px 0 0 -22px; border-style: dashed;
  border-color: rgba(156, 196, 255, 0.7); }
.cur-ring.down { width: 16px; height: 16px; margin: -8px 0 0 -8px; background: rgba(156, 196, 255, 0.18); }
/* it fires like a neuron: the dot flashes now and then, a click sends out a burst, and moving leaves faint sparks */
.has-cursor .cur-dot { animation: cur-fire 2.6s infinite; }
@keyframes cur-fire {
  0%, 82%, 100% { box-shadow: 0 0 10px 2px rgba(156, 196, 255, 0.9); background: #eef1f5; }
  86% { box-shadow: 0 0 22px 7px rgba(190, 220, 255, 1), 0 0 44px 14px rgba(156, 196, 255, 0.45); background: #fff; }
  90% { box-shadow: 0 0 8px 1px rgba(156, 196, 255, 0.7); }
  93% { box-shadow: 0 0 18px 5px rgba(190, 220, 255, 0.95); background: #fff; }
}
.cur-burst, .cur-spark { position: fixed; left: 0; top: 0; pointer-events: none; z-index: 9998; }
.cur-burst i { position: absolute; width: 20px; height: 20px; margin: -10px 0 0 -10px; border-radius: 50%;
  border: 1.5px solid rgba(190, 220, 255, 0.95); box-shadow: 0 0 14px rgba(156, 196, 255, 0.8);
  animation: cur-burst 0.6s ease-out forwards; }
@keyframes cur-burst { from { transform: scale(0.4); opacity: 1; } to { transform: scale(4.2); opacity: 0; } }
.cur-spark i { position: absolute; width: 3px; height: 3px; margin: -1.5px 0 0 -1.5px; border-radius: 50%;
  background: #dce9ff; box-shadow: 0 0 6px 1px rgba(156, 196, 255, 0.9); animation: cur-spark 0.7s ease-out forwards; }
@keyframes cur-spark { to { transform: translate(var(--dx), var(--dy)) scale(0.2); opacity: 0; } }
@media (prefers-reduced-motion: reduce) { .has-cursor .cur-dot { animation: none; } }
/* the principles grid: five across on wide screens, and no filled gap where a row is short */
.principles ol { background: none; border: none; gap: 0; }
.principles li { border: 1px solid var(--line); margin: 0 -1px -1px 0; }
@media (min-width: 1100px) { .principles ol { grid-template-columns: repeat(5, minmax(0, 1fr)); } }
@media (max-width: 760px) {
  .status { display: flex !important; gap: 14px; font-size: 11px; letter-spacing: 0.16em; }
  .prose section, .faq .qa { grid-template-columns: 1fr; }
}
@media (max-width: 760px) { .bar { flex-wrap: wrap; row-gap: 14px; } }
@media (max-width: 480px) {
  h1, .page-head h1 { font-stretch: 100%; font-size: clamp(30px, 9.4vw, 44px); }
  .about h2, .principles h2, .faq h2 { font-stretch: 105%; font-size: clamp(26px, 8vw, 40px); }
  .next p { font-stretch: 105%; }
}
"""

MARK = (SRC / "mark.svg").read_text()
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=Instrument+Sans:'
         'wght@400;500&display=swap" rel="stylesheet">')

ORG = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Valugent", "url": f"{SITE}/",
       "logo": f"{SITE}/apple-touch-icon.png", "email": EMAIL,
       "description": "Valugent is an AI agent factory building values-driven, trustworthy AI agents.",
       "slogan": "Values-driven AI agents"}


def ld(*items):
    return ('<script type="application/ld+json">\n'
            + json.dumps({"@context": "https://schema.org", "@graph": list(items)}, indent=1) + "\n</script>")


def crumbs(name, path):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Valugent", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": f"{SITE}{path}"}]}


def nav(here):
    links = [("/approach/", "How it works"), ("/principles/", "Principles"), ("/#faq", "FAQ")]
    return ('<nav class="status" aria-label="Main">' + "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == here else ""}>{t}</a>' for h, t in links) + "</nav>")


CURSOR_JS = r"""<script>
(() => {
  // the cursor: on a mouse or trackpad only; touch screens and keyboards keep their own
  if (!matchMedia("(pointer: fine)").matches) return;
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const dot = document.createElement("div"), ring = document.createElement("div");
  dot.className = "cur-dot"; ring.className = "cur-ring";
  document.body.append(dot, ring);
  let x = -100, y = -100, rx = -100, ry = -100, shown = false;
  addEventListener("pointermove", e => {
    if (e.pointerType !== "mouse") return;
    x = e.clientX; y = e.clientY;
    if (!shown) { shown = true; rx = x; ry = y; }
    document.documentElement.classList.add("has-cursor");   // back on as soon as the mouse returns to the page
    const t = e.target;
    ring.classList.toggle("link", !!t.closest("a, button"));
    ring.classList.toggle("brain", !t.closest("a, button") && !!t.closest(".hero"));
  });
  function flash(cls, life) {                               // a short-lived spot of light where the cursor is
    const el = document.createElement("div"), i = document.createElement("i");
    el.className = cls; el.style.transform = `translate(${x}px, ${y}px)`;
    if (cls === "cur-spark") {
      const a = Math.random() * Math.PI * 2, r = 8 + Math.random() * 14;
      i.style.setProperty("--dx", `${Math.cos(a) * r}px`); i.style.setProperty("--dy", `${Math.sin(a) * r}px`);
    }
    el.append(i); document.body.append(el);
    setTimeout(() => el.remove(), life);
  }
  let lastSpark = 0, sx = 0, sy = 0;
  if (!still) addEventListener("pointermove", e => {
    if (e.pointerType !== "mouse") return;
    const now = performance.now(), d = Math.hypot(e.clientX - sx, e.clientY - sy);
    if (now - lastSpark > 45 && d > 18) { lastSpark = now; sx = e.clientX; sy = e.clientY; flash("cur-spark", 750); }
  });
  addEventListener("pointerdown", e => { ring.classList.add("down"); if (!still && e.pointerType === "mouse") flash("cur-burst", 650); });
  addEventListener("pointerup", () => ring.classList.remove("down"));
  document.addEventListener("mouseleave", () => document.documentElement.classList.remove("has-cursor"));
  (function move() {
    rx += (x - rx) * (still ? 1 : 0.18); ry += (y - ry) * (still ? 1 : 0.18);
    dot.style.transform = `translate(${x}px, ${y}px)`;
    ring.style.transform = `translate(${rx}px, ${ry}px)`;
    requestAnimationFrame(move);
  })();
})();
</script>"""


def page(path, title, desc, body, *, schema, here="", home=False):
    url = f"{SITE}{path}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#05070b">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Valugent">
<meta property="og:locale" content="en_AU">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Valugent: values-driven AI agents">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/og.png">
{FONTS}
{ld(*schema)}
<style>
{CSS}
</style>
</head>
<body{'' if home else ' class="page"'}>
<header class="bar">
  <a href="/" aria-label="Valugent home">{MARK}</a>
  {nav(here)}
</header>
<main>
{body}
</main>
<footer>
  <span><strong>Valugent</strong> &middot; AI agent factory &middot; in development</span>
  <span>Contact <a href="mailto:{EMAIL}">{EMAIL}</a></span>
  <span><a href="/approach/">How it works</a> &nbsp; <a href="/principles/">Principles</a></span>
  <span>&copy; 2026 Valugent</span>
</footer>
{CURSOR_JS}
{'<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" defer></script>' + chr(10) + '<script src="/brain.js" defer></script>' if home else ''}
</body>
</html>
"""


# ------------------------------------------------------------------ the questions people ask (home page, FAQPage)
FAQ = [
    ("What is an AI agent factory?",
     "An AI agent factory builds AI agents from a specification instead of by hand. At Valugent, each agent starts as a "
     "plain written definition: what it is for, what it may do and what it must never do. The factory turns that "
     "definition into a working agent, with the same limits, checks and record every time."),
    ("What makes a Valugent AI agent trustworthy?",
     "Trust comes from what surrounds the model, not from the model alone. Each agent runs in a sealed environment, can "
     "use only the tools it is allowed, needs approval for the exact action it takes, and writes every step to a ledger "
     "that can be checked later."),
    ("What does values-driven mean for an AI agent?",
     "It means an agent's purpose and limits come first. They are written down before the agent is given any power, and "
     "the factory holds the agent to them: it refuses rather than guesses, and it stays inside the authority it was "
     "given."),
    ("Which AI models does Valugent work with?",
     "The factory reaches the model through a single interface, so an agent's definition is not tied to one AI model or "
     "provider. The same definition is meant to behave the same way on any model, and to keep working as models get "
     "stronger."),
    ("What does an AI agent do when it is not sure?",
     "It says so. A Valugent agent rests its answers on the documents and checks behind them. When the evidence is not "
     "there, it reports that it cannot confirm the answer instead of guessing."),
    ("Can a Valugent agent act without a person's approval?",
     "Not for actions that matter. An approval is bound to the exact action a person agreed to, so an agent cannot reuse "
     "it for anything else, and every approval is recorded."),
    ("Is Valugent available now?",
     f"Not yet. Valugent is in development, and the first agents are being built and tested for our own use. To get in "
     f"touch, write to {EMAIL}."),
]


def faq_html():
    return ('  <section class="faq" id="faq">\n    <p class="label">Questions</p>\n'
            '    <h2>AI agents, answered</h2>\n    <dl>\n' + "".join(
                f'      <div class="qa"><dt>{q}</dt><dd>{a}</dd></div>\n' for q, a in FAQ) + "    </dl>\n  </section>")


FAQ_LD = {"@type": "FAQPage", "@id": f"{SITE}/#faq", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}


# ------------------------------------------------------------------ home
HOME_DESC = ("Valugent is an AI agent factory. It turns a plain written definition into a values-driven AI agent that "
             "acts only within its authority, rests its answers on evidence, and keeps a record of everything it does.")
HOME = f"""  <section class="hero">
    <canvas id="brain" aria-hidden="true"></canvas>
    <div class="hero-copy">
      <h1>Values-driven<br>AI agents</h1>
      <p class="lede">Valugent is an AI agent factory. It builds AI agents that act only within the authority they are given, rest their answers on evidence, and keep a record of everything they do.</p>
      <p class="cta"><a class="btn" href="mailto:{EMAIL}?subject=Early%20access">Get early access</a><span>Agents are in development. Leave your email and we will be in touch.</span></p>
    </div>
  </section>

  <section class="about" id="about">
    <div>
      <p class="label">What we are building</p>
      <h2>An AI agent factory you can trust</h2>
    </div>
    <div class="copy">
      <p>Valugent is building a factory for AI agents. Each agent starts as a plain written definition: what it is for, what it may do, and what it must never do. The factory turns that definition into a working agent.</p>
      <p>The aim is an AI agent that behaves the same way on any model, acts only within the authority it was given, and can show what it did. AI models keep getting more powerful, and they are not fully predictable. Valugent supplies what the model lacks: limits, evidence, checks and a record.</p>
      <p>The work is in development. The first agents are being built and tested for our own use.</p>
      <p><a class="more" href="/approach/">How the AI agent factory works</a></p>
    </div>
  </section>

  <section class="band" aria-label="How a Valugent AI agent is put together">
    <div class="part">
      <h2>The model</h2>
      <p>The power. Rented from a provider, and replaceable.</p>
    </div>
    <div class="part">
      <h2>The harness</h2>
      <p>The reins and gates. The agent goes only where it is allowed.</p>
    </div>
    <div class="part">
      <h2>The judgement</h2>
      <p>Evidence and checks that steer the power, and a rule to refuse rather than guess.</p>
    </div>
    <div class="part">
      <h2>The record</h2>
      <p>A ledger of what the agent actually did, not its own account of it.</p>
    </div>
  </section>

  <section class="principles" id="principles">
    <p class="label">Principles</p>
    <h2>Values before power</h2>
    <ol>
      <li><span>01</span><h3>Purpose first</h3><p>An agent's purpose and limits are written down before it is given any power.</p></li>
      <li><span>02</span><h3>Approval for each action</h3><p>An agent carries out only the exact action a person approved, and nothing else.</p></li>
      <li><span>03</span><h3>Evidence, not guesses</h3><p>Answers rest on the documents and checks behind them. When the evidence is not there, the agent says so.</p></li>
      <li><span>04</span><h3>A record of everything</h3><p>Every action is written to a ledger that can be checked later.</p></li>
      <li><span>05</span><h3>Not tied to one model</h3><p>An agent's definition belongs to its owner and can move between AI models.</p></li>
    </ol>
    <a class="more" href="/principles/">Read the principles in full</a>
  </section>

{faq_html()}
"""

# ------------------------------------------------------------------ how it works
APPROACH_DESC = ("How the Valugent AI agent factory builds trustworthy AI agents: a written definition, a sealed harness, "
                 "evidence-based judgement, approval for each exact action, and a ledger of everything the agent does.")
STEPS = [
    ("Start with a definition",
     ["Every AI agent begins as a plain written definition, kept as a versioned file. It says what the agent is for, what "
      "it may do, what it must never do, and which actions need a person's approval.",
      "The definition holds no personal data, so it can be read, reviewed and changed like any other document. The "
      "factory builds the agent from it, the same way every time."]),
    ("A sealed harness",
     ["The agent works inside a sealed environment. It can reach only the tools its definition allows, through one "
      "gateway that checks each request, and nothing leaves that environment without permission.",
      "Logins and keys stay with the factory, never with the agent. The model can be as capable as it likes: the harness "
      "decides where it may go."]),
    ("Judgement built from evidence",
     ["An agent's answers rest on the documents and checks behind them. Figures are checked against their sources, and "
      "an independent review step looks at the answer before it stands.",
      "When the evidence is not there, the agent says so instead of guessing. A clear \"I cannot confirm this\" is worth "
      "more than a confident mistake."]),
    ("Approval for the exact action",
     ["For anything that matters, an agent proposes and a person decides. An approval is bound to the exact action that "
      "was shown, so it cannot be reused for something else."]),
    ("A ledger as the flight recorder",
     ["Every step an agent takes is written to a ledger: what it read, what it ran, what it proposed and who approved "
      "it. The ledger is built so that a changed or missing entry shows.",
      "It is the proof of what the agent actually did, not the agent's own account of it."]),
    ("Any model, the same agent",
     ["The factory reaches AI models through a single interface. An agent's definition is not tied to one provider, so "
      "it can move between models and keep its limits, checks and record.",
      "Models get stronger every few months. The factory is built around evidence and checks rather than around today's "
      "model's weaknesses, so a stronger model makes a better agent, not a riskier one."]),
]


def numbered(items):
    return "\n".join(
        f'    <section><h2><span>{i:02d}</span>{t}</h2><div class="body">' + "".join(f"<p>{p}</p>" for p in ps)
        + "</div></section>" for i, (t, ps) in enumerate(items, 1))


APPROACH = f"""  <div class="page-head">
    <p class="crumbs"><a href="/">Valugent</a> / How it works</p>
    <h1>How the AI agent factory works</h1>
    <p class="lede">An AI model is like an untamed dragon: enormous power, not fully predictable, and rented. The Valugent factory supplies the rest: the reins, the rider's judgement and the flight recorder.</p>
  </div>
  <div class="prose">
{numbered(STEPS)}
  </div>
  <div class="next"><p>The values behind every Valugent agent</p><a class="more" href="/principles/">Read the principles</a></div>
"""

# ------------------------------------------------------------------ principles
PRINCIPLES_DESC = ("The principles behind Valugent's values-driven AI agents: purpose first, approval for each action, "
                   "evidence not guesses, a record of everything, separate data, and no lock-in to one AI model.")
PRINCIPLES = [
    ("Purpose first", ["An AI agent's purpose and limits are written down before it is given any power. What it may do, "
                       "and what it must never do, are part of the agent, not an afterthought."]),
    ("Approval for each action", ["An agent carries out only the exact action a person approved. Approval is never a "
                                  "blank cheque: change the action and it needs approving again."]),
    ("Evidence, not guesses", ["Answers rest on the documents and checks behind them. When the evidence is not there, "
                               "the agent says it cannot confirm the answer. Refusing is better than guessing."]),
    ("A record of everything", ["Every action is written to a ledger that can be checked later. Trust is earned from "
                                "the record, not from what the agent says about itself."]),
    ("Each agent's data kept apart", ["Every agent's data and records are kept separate from every other's, and an "
                                      "agent's definition carries no personal data."]),
    ("Not tied to one model", ["An agent's definition belongs to its owner and can move between AI models and "
                               "providers. No agent should depend on one company's model to keep its values."]),
    ("Built for stronger models", ["AI models get stronger every few months. Valugent is built to work with a stronger "
                                   "model, not against it, so the same limits hold as the power grows."]),
]
PRINCIPLES_HTML = f"""  <div class="page-head">
    <p class="crumbs"><a href="/">Valugent</a> / Principles</p>
    <h1>Principles for values-driven AI agents</h1>
    <p class="lede">An AI agent is only as trustworthy as the rules it cannot break. These are the rules every Valugent agent is built on.</p>
  </div>
  <div class="prose">
{numbered(PRINCIPLES)}
  </div>
  <div class="next"><p>How the factory holds an agent to them</p><a class="more" href="/approach/">See how it works</a></div>
"""

PAGES = [
    ("/", "index.html", "Valugent | AI agent factory for values-driven, trustworthy AI agents", HOME_DESC, HOME,
     [ORG, {"@type": "WebSite", "@id": f"{SITE}/#site", "name": "Valugent", "url": f"{SITE}/", "publisher": {"@id": f"{SITE}/#org"},
            "inLanguage": "en"}, FAQ_LD], "", True, "1.0"),
    ("/approach/", "approach/index.html", "How the AI agent factory works | Valugent", APPROACH_DESC, APPROACH,
     [ORG, crumbs("How it works", "/approach/"), {"@type": "WebPage", "name": "How the AI agent factory works",
                                                   "url": f"{SITE}/approach/", "about": {"@id": f"{SITE}/#org"}}],
     "/approach/", False, "0.8"),
    ("/principles/", "principles/index.html", "Principles for values-driven AI agents | Valugent", PRINCIPLES_DESC,
     PRINCIPLES_HTML,
     [ORG, crumbs("Principles", "/principles/"), {"@type": "WebPage", "name": "Principles for values-driven AI agents",
                                                  "url": f"{SITE}/principles/", "about": {"@id": f"{SITE}/#org"}}],
     "/principles/", False, "0.8"),
]

for path, out, title, desc, body, schema, here, home, prio in PAGES:
    f = ROOT / out
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(page(path, title, desc, body, schema=schema, here=here, home=home))

(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url><loc>{SITE}{p[0]}</loc><lastmod>{UPDATED}</lastmod><priority>{p[8]}</priority></url>\n" for p in PAGES)
                                  + "</urlset>\n")
print("built", [p[1] for p in PAGES])
