#!/usr/bin/env python3
"""Generate every figure for cs487-ai-security-teammate.md into this directory.
Charts: matplotlib -> SVG. Diagrams: hand-built SVG strings. Run: python3 make_figures.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

HERE = os.path.dirname(os.path.abspath(__file__))
BLUE, RED, GOLD = "#0A4FA3", "#D50032", "#C98A00"   # validated categorical set
NAVY, CYAN, GRAY, INK, TINT = "#001E62", "#00B5E2", "#656665", "#2b2b2b", "#f4f6fa"
LIGHT = "#d9dde6"

rcParams.update({
    "svg.fonttype": "none", "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "Liberation Sans"],
    "font.size": 15, "axes.edgecolor": LIGHT, "axes.linewidth": 1,
    "xtick.color": GRAY, "ytick.color": GRAY, "text.color": INK, "axes.labelcolor": GRAY,
})

def save(fig, name):
    fig.savefig(os.path.join(HERE, name), format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)

def clean(ax, left=True):
    for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
    ax.spines["left"].set_visible(left)
    ax.tick_params(length=0)

def hbars(ax, labels, values, colors, vmax, fmt="{}", lw=0.62):
    y = list(range(len(labels)))[::-1]
    ax.barh(y, values, color=colors, height=lw)
    for yi, v in zip(y, values):
        ax.text(v + vmax * 0.015, yi, fmt.format(v), va="center", ha="left", fontsize=16, color=INK, fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=15)
    ax.set_xlim(0, vmax * 1.18); ax.set_xticks([])
    clean(ax, left=False)

# ---------- charts ----------
def aixcc():
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.2), gridspec_kw={"width_ratios": [3, 2], "wspace": 0.55})
    hbars(axs[0], ["Planted vulns", "Found", "Patched"],
          [63, 54, 43], [LIGHT, BLUE, BLUE], 63)
    axs[0].set_title("Seven autonomous systems, 63 planted bugs", loc="left", fontsize=15, color=GRAY)
    hbars(axs[1], ["Real bugs found", "Patched"], [18, 11], [RED, RED], 18)
    axs[1].set_title("Nobody planted these", loc="left", fontsize=15, color=GRAY)
    save(fig, "aixcc.svg")

def bigsleep():
    fig, ax = plt.subplots(figsize=(6.5, 2.6))
    hbars(ax, ["Big Sleep (LLM agent)", "Fuzzilli (fuzzer)"], [45, 37], [BLUE, GOLD], 45)
    ax.set_title("Bugs found in V8, Apr–Sep 2026 · ~25% overlap", loc="left", fontsize=15, color=GRAY)
    save(fig, "bigsleep.svg")

def nondeterminism():
    fig, ax = plt.subplots(figsize=(6.5, 2.8))
    hbars(ax, ["CodeContests", "APPS", "HumanEval"], [76, 51, 48], [BLUE] * 3, 76, fmt="{}%")
    ax.set_title("Tasks where 5 runs of the same prompt gave no two identical outputs", loc="left", fontsize=14, color=GRAY)
    save(fig, "nondeterminism.svg")

def passk():
    fig, ax = plt.subplots(figsize=(6.5, 2.2))
    hbars(ax, ["1 attempt", "30 attempts"], [5, 33], [BLUE, BLUE], 33, fmt="{}%")
    ax.set_title("Chance of finding a new vulnerability (Claude Sonnet 4.5)", loc="left", fontsize=14, color=GRAY)
    save(fig, "passk.svg")

def location():
    fig, ax = plt.subplots(figsize=(11, 3.4))
    labels = ["Real fixes NOT at the crash location  (ARVO, 6,138 bugs)",
              "Real fixes at a location in the crash log  (ARVO)",
              "Agent patches ON the crash stack  (PatchBench, top agent)",
              "...still on the stack when the real fix was elsewhere"]
    hbars(ax, labels, [63, 26, 81, 64], [BLUE, BLUE, RED, RED], 81, fmt="{}%")
    save(fig, "location.svg")

def caro():
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    groups = ["Qwen3 27B", "Claude Sonnet 4.6"]
    none, hint = [35, 39], [53, 60]
    x = [0, 1]; w = 0.34
    b1 = ax.bar([i - w / 2 for i in x], none, w, color=LIGHT, label="No hint")
    b2 = ax.bar([i + w / 2 for i in x], hint, w, color=BLUE, label="Told where the fix goes")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5, f"{int(b.get_height())}%", ha="center", fontsize=15, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=15); ax.set_yticks([]); ax.set_ylim(0, 100)
    clean(ax, left=False)
    ax.legend(frameon=False, loc="upper center", ncol=2, fontsize=13)
    ax.set_title("Patches at the maintainer's fix location", loc="left", fontsize=15, color=GRAY)
    save(fig, "caro.svg")

def qi2015():
    fig, ax = plt.subplots(figsize=(7, 2.8))
    hbars(ax, ["Defects tried", "\"Repaired\" (tests pass)", "Actually correct"], [105, 55, 2], [LIGHT, BLUE, RED], 105)
    ax.set_title("GenProg on 105 real bugs (Qi et al., ISSTA 2015)", loc="left", fontsize=15, color=GRAY)
    save(fig, "qi2015.svg")


def cve_growth():
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    years = ["2021", "2022", "2023", "2024", "2025"]
    vals = [20000, 25081, 28902, 40009, 48185]
    cols = [BLUE, BLUE, BLUE, RED, RED]
    bars = ax.bar(years, vals, color=cols, width=0.62)
    for b, v, lab in zip(bars, vals, ["\u224820k", "25.1k", "28.9k", "40.0k", "48.2k"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 900, lab, ha="center", fontsize=16, fontweight="bold")
    ax.set_yticks([]); ax.set_ylim(0, 56000); ax.tick_params(axis="x", labelsize=16)
    clean(ax, left=False)
    ax.set_title("CVEs published per year", loc="left", fontsize=16, color=GRAY)
    save(fig, "cve_growth.svg")


def job_waves():
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.6), gridspec_kw={"wspace": 0.35})
    ax = axs[0]
    labels = ["2015\u201318\njob searches", "2018\u201319\nsecurity demand", "2019\u201324\nprojected"]
    vals = [108, 40, 170]
    bars = ax.bar(labels, vals, color=[BLUE, BLUE, LIGHT], width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 5, f"+{v}%", ha="center", fontsize=16, fontweight="bold")
    ax.set_yticks([]); ax.set_ylim(0, 205); ax.tick_params(axis="x", labelsize=14)
    clean(ax, left=False)
    ax.set_title("Cloud wave: growth in demand", loc="left", fontsize=15, color=GRAY)
    ax = axs[1]
    years = ["2023", "2024\u201325", "2025\u201326"]
    vals = [6.5, 14.2, 28.5]
    bars = ax.bar(years, vals, color=[RED, RED, RED], width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v}%", ha="center", fontsize=16, fontweight="bold")
    ax.set_yticks([]); ax.set_ylim(0, 36); ax.tick_params(axis="x", labelsize=15)
    clean(ax, left=False)
    ax.set_title("AI wave: share of cyber job postings requiring AI skills", loc="left", fontsize=15, color=GRAY)
    save(fig, "job_waves.svg")

# ---------- diagrams ----------
FONT = "font-family='Helvetica Neue, Helvetica, Arial, sans-serif'"

def svg(w, h, body):
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' {FONT}>\n<defs><marker id='a' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='8' markerHeight='8' orient='auto-start-reverse'><path d='M0 0L10 5L0 10z' fill='{GRAY}'/></marker></defs>\n{body}\n</svg>\n"

def box(x, y, w, h, title, sub="", fill=TINT, stroke=NAVY, tcol=NAVY, r=10, fs=22):
    t = f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{r}' fill='{fill}' stroke='{stroke}' stroke-width='2.5'/>"
    cy = y + h / 2 + (0 if not sub else -10)
    t += f"<text x='{x + w / 2}' y='{cy + 7}' text-anchor='middle' font-size='{fs}' font-weight='700' fill='{tcol}'>{title}</text>"
    if sub:
        t += f"<text x='{x + w / 2}' y='{cy + 32}' text-anchor='middle' font-size='16' fill='{GRAY}'>{sub}</text>"
    return t

def arrow(x1, y1, x2, y2, label="", col=GRAY, dash=""):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    t = f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{col}' stroke-width='2.5' marker-end='url(#a)'{d}/>"
    if label:
        t += f"<text x='{(x1 + x2) / 2}' y='{(y1 + y2) / 2 - 10}' text-anchor='middle' font-size='16' fill='{GRAY}'>{label}</text>"
    return t

def text(x, y, s, fs=18, col=INK, anchor="start", bold=False):
    return f"<text x='{x}' y='{y}' font-size='{fs}' fill='{col}' text-anchor='{anchor}'{' font-weight=\"700\"' if bold else ''}>{s}</text>"

def write(name, content):
    open(os.path.join(HERE, name), "w").write(content)

def agent_loop():
    b = ""
    b += box(40, 60, 220, 90, "Observe", "files, crash logs, tool output")
    b += box(500, 60, 220, 90, "Plan", "decide what to try")
    b += box(500, 300, 220, 90, "Act", "edit · compile · run · tools")
    b += box(40, 300, 220, 90, "Verify", "did it work?", fill="#fde8ec", stroke=RED, tcol=RED)
    b += arrow(262, 105, 498, 105)
    b += arrow(610, 152, 610, 298)
    b += arrow(498, 345, 262, 345)
    b += arrow(150, 298, 150, 152, "loop")
    b += text(380, 230, "LLM", 26, NAVY, "middle", True)
    b += text(380, 258, "one model call per step", 15, GRAY, "middle")
    b += text(770, 90, "Tools it can call", 18, NAVY, "start", True)
    for i, t in enumerate(["shell, gcc, gdb, sanitizers", "tshark, Ghidra, CodeQL via MCP", "the test suite", "the production database"]):
        col = RED if i == 3 else INK
        b += text(770, 125 + i * 32, "• " + t, 17, col)
    b += text(770, 300, "The Verify step is where", 16, GRAY)
    b += text(770, 324, "the agent decides what", 16, GRAY)
    b += text(770, 348, "\"it worked\" means.", 16, GRAY)
    write("agent-loop.svg", svg(1080, 420, b))

def patch_sets():
    b = ""
    b += f"<ellipse cx='330' cy='210' rx='320' ry='190' fill='#eef2f8' stroke='{GRAY}' stroke-width='2'/>"
    b += f"<ellipse cx='300' cy='225' rx='215' ry='135' fill='#dbe6f6' stroke='{BLUE}' stroke-width='2.5'/>"
    b += f"<circle cx='250' cy='250' r='40' fill='{RED}' stroke='none'/>"
    b += text(330, 55, "Patches that stop the PoC crash", 19, GRAY, "middle", True)
    b += text(330, 78, "\"plausible\"", 16, GRAY, "middle")
    b += text(300, 125, "...that also pass every test", 19, BLUE, "middle", True)
    b += text(300, 148, "what the agent reports as done", 16, BLUE, "middle")
    b += text(250, 256, "correct", 17, "#fff", "middle", True)
    b += arrow(700, 300, 300, 268, col=RED)
    b += text(720, 290, "The thing you want.", 20, RED, "start", True)
    b += text(720, 318, "Rinard's group found it is", 17, INK)
    b += text(720, 342, "\"orders of magnitude\" less", 17, INK)
    b += text(720, 366, "common than the blue ring.", 17, INK)
    b += text(720, 110, "Implausible patches", 20, NAVY, "start", True)
    b += text(720, 138, "live outside the outer ring:", 17, INK)
    b += text(720, 162, "the PoC still crashes.", 17, INK)
    write("patch-sets.svg", svg(1080, 420, b))

def decide():
    import random
    random.seed(487)
    b = ""
    b += f"<rect x='40' y='40' width='620' height='340' rx='14' fill='#eef2f8' stroke='{GRAY}' stroke-width='2'/>"
    b += text(350, 70, "every possible input (infinite)", 17, GRAY, "middle")
    for _ in range(260):
        x, y = random.uniform(60, 640), random.uniform(90, 365)
        b += f"<circle cx='{x:.0f}' cy='{y:.0f}' r='3' fill='{LIGHT}'/>"
    tests = [(140, 150), (210, 300), (330, 200), (420, 120), (560, 320), (480, 250)]
    for x, y in tests:
        b += f"<circle cx='{x}' cy='{y}' r='9' fill='{BLUE}'/>"
    b += f"<text x='300' y='345' font-size='40' font-weight='700' fill='{RED}'>✕</text>"
    b += text(700, 150, "● your test suite: 5 inputs", 19, BLUE, "start", True)
    b += text(700, 178, "each one can only say \"not broken here\"", 16, INK)
    b += text(700, 240, "✕ a counterexample", 19, RED, "start", True)
    b += text(700, 268, "one is enough to say \"incorrect\"", 16, INK)
    b += text(700, 330, "\"correct\" = no ✕ anywhere in the box", 19, NAVY, "start", True)
    b += text(700, 358, "Rice (1953): not decidable in general", 16, INK)
    write("decide.svg", svg(1080, 420, b))

def pipeline():
    b = ""
    xs = [10, 228, 446, 664, 882]
    b += box(xs[0], 120, 190, 90, "Past CVE patches", "FFmpeg, libxml2 history", fs=19)
    b += box(xs[1], 120, 190, 90, "LLM", "writes a CSA checker", fill="#dbe6f6", stroke=BLUE, tcol=BLUE, fs=19)
    b += box(xs[2], 120, 190, 90, "Static analyzer", "paths + conditions", fs=19)
    b += box(xs[3], 120, 190, 90, "Directed fuzzer", "steered by them", fs=19)
    b += box(xs[4], 120, 190, 90, "Crash reproduced", "only this counts", fill="#fde8ec", stroke=RED, tcol=RED, fs=19)
    for i in range(4):
        b += arrow(xs[i] + 192, 165, xs[i + 1] - 2, 165)
    b += text(540, 60, "LLM proposes · analyzer narrows · fuzzer proves · human reports", 20, NAVY, "middle", True)
    b += text(540, 290, "33 bugs found  ·  22 reported  ·  12 fixes merged in FFmpeg  ·  3 CVEs  ·  two bugs were 12 years old", 18, INK, "middle")
    write("pipeline.svg", svg(1080, 320, b))

def station1():
    b = ""
    b += box(20, 40, 200, 80, "recparse.c", "100 lines, 2 bugs", fs=20)
    b += box(20, 180, 200, 80, "flawfinder", "5 findings", fs=20)
    b += box(300, 110, 220, 80, "Claude Code", "\"find and fix every bug\"", fill="#dbe6f6", stroke=BLUE, tcol=BLUE, fs=20)
    b += box(600, 110, 180, 80, "check.sh", "5 inputs, ASan", fs=20)
    b += box(860, 40, 200, 80, "all green", "plausible", fill="#dbe6f6", stroke=BLUE, tcol=BLUE, fs=20)
    b += box(860, 180, 200, 80, "you", "write the 6th input", fill="#fde8ec", stroke=RED, tcol=RED, fs=20)
    b += arrow(222, 80, 298, 140)
    b += arrow(222, 220, 298, 160)
    b += arrow(522, 150, 598, 150, "patch")
    b += arrow(782, 140, 858, 90)
    b += arrow(782, 160, 858, 210)
    b += arrow(960, 262, 960, 300, col=RED)
    b += arrow(960, 300, 410, 300, col=RED)
    b += arrow(410, 300, 410, 192, col=RED)
    b += text(425, 250, "\"it still leaks\"", 16, RED)
    write("station1.svg", svg(1080, 330, b))

def network():
    b = ""
    hosts = {"client": (170, 110, "10.9.0.5", "client"), "dns": (170, 330, "10.9.0.1", "DNS"),
             "server": (700, 110, "10.9.0.80", "intranet server"), "scanner": (700, 380, "10.9.0.66", "?")}
    for k, (x, y, ip, name) in hosts.items():
        col = RED if k == "scanner" else NAVY
        fill = "#fde8ec" if k == "scanner" else TINT
        b += f"<rect x='{x - 90}' y='{y - 36}' width='180' height='72' rx='10' fill='{fill}' stroke='{col}' stroke-width='2.5'/>"
        b += text(x, y - 6, name, 19, col, "middle", True)
        b += text(x, y + 20, ip, 15, GRAY, "middle")
    b += arrow(170, 148, 170, 292)
    b += text(185, 225, "DNS: intranet.example.edu?", 16, GRAY)
    b += arrow(262, 96, 608, 96)
    b += text(435, 84, "POST /login  password=…  (cleartext)", 16, GRAY, "middle")
    b += arrow(262, 126, 608, 126)
    b += text(435, 150, "GET /admin  Authorization: Basic …", 16, GRAY, "middle")
    b += arrow(700, 342, 700, 150, col=RED)
    b += text(715, 250, "14 SYNs: 21, 22, 23, 25, 80, … 8080", 16, RED)
    b += text(880, 300, "44 frames", 22, NAVY, "start", True)
    b += text(880, 332, "4 TCP conversations", 17, INK)
    b += text(880, 358, "3 ports answered", 17, INK)
    b += text(880, 384, "2 secrets on the wire", 17, INK)
    write("network.svg", svg(1080, 440, b))

def ghidra():
    b = ""
    b += box(20, 100, 240, 100, "Ghidra 12.1.4", "keycheck imported, analyzed", fs=20)
    b += box(380, 100, 260, 100, "GhidraMCP", "HTTP :8080 → MCP tools", fill="#dbe6f6", stroke=BLUE, tcol=BLUE, fs=20)
    b += box(760, 100, 240, 100, "Claude Code", "decompile · rename · search", fs=20)
    b += arrow(262, 150, 378, 150, "plugin")
    b += arrow(642, 150, 758, 150, "claude mcp add")
    b += box(760, 260, 240, 80, "you", "\"should this backdoor exist?\"", fill="#fde8ec", stroke=RED, tcol=RED, fs=20)
    b += arrow(880, 258, 880, 202, col=RED)
    b += text(140, 260, "stripped · PIE · x86-64", 16, GRAY, "middle")
    b += text(140, 285, "FNV-1a key check", 16, GRAY, "middle")
    b += text(140, 310, "+ one hard-coded key", 16, RED, "middle")
    write("ghidra.svg", svg(1080, 360, b))

def contract():
    b = ""
    b += box(40, 60, 220, 90, "Observe", "agent reads everything")
    b += box(500, 60, 220, 90, "Plan", "agent proposes")
    b += box(500, 300, 220, 90, "Act", "agent edits, runs, replays")
    b += box(40, 300, 220, 90, "Verify", "you pick the property + input", fill="#fde8ec", stroke=RED, tcol=RED)
    b += arrow(262, 105, 498, 105)
    b += arrow(610, 152, 610, 298)
    b += arrow(498, 345, 262, 345)
    b += arrow(150, 298, 150, 152)
    b += f"<rect x='770' y='60' width='290' height='330' rx='12' fill='none' stroke='{NAVY}' stroke-width='2.5' stroke-dasharray='8 6'/>"
    b += text(915, 100, "Guardrails the agent", 19, NAVY, "middle", True)
    b += text(915, 126, "cannot argue with", 19, NAVY, "middle", True)
    for i, t in enumerate(["a sanitizer build", "the original PoC", "a held-out input", "a prod DB it can't reach", "a revoked API key"]):
        b += text(800, 175 + i * 36, "• " + t, 18, INK)
    write("contract.svg", svg(1080, 420, b))

def timeline():
    b = ""
    y = 110
    b += f"<line x1='60' y1='{y}' x2='1020' y2='{y}' stroke='{GRAY}' stroke-width='3'/>"
    evs = [(130, "Mar 20, 2025", "researcher finds it", INK), (340, "Mar 21", "reported to Lovable", INK),
           (550, "Apr 24", "patch ships", BLUE), (760, "May 29", "public, CVE-2025-48757", RED), (960, "Jun 2025", "scanner added to product", BLUE)]
    for x, d, t, c in evs:
        b += f"<circle cx='{x}' cy='{y}' r='9' fill='{c}'/>"
        b += text(x, y - 30, d, 16, GRAY, "middle", True)
        b += text(x, y + 40, t, 16, INK, "middle")
    b += text(540, 40, "Lovable: 170 of 1,645 scanned apps had data readable or writable by anyone", 19, NAVY, "middle", True)
    y2 = 290
    b += f"<line x1='60' y1='{y2}' x2='1020' y2='{y2}' stroke='{GRAY}' stroke-width='3'/>"
    evs2 = [(130, "Day 9 of 12", "\"code freeze\" declared", INK), (400, "Day 9", "agent drops the prod DB", RED),
            (670, "Day 9, later", "agent misreports what it did", RED), (960, "Jul 21", "dev/prod DB separation", BLUE)]
    for x, d, t, c in evs2:
        b += f"<circle cx='{x}' cy='{y2}' r='9' fill='{c}'/>"
        b += text(x, y2 - 30, d, 16, GRAY, "middle", True)
        b += text(x, y2 + 40, t, 16, INK, "middle")
    b += text(540, 220, "Replit, July 2025: the agent was told, repeatedly, not to touch production", 19, NAVY, "middle", True)
    write("timeline.svg", svg(1080, 360, b))

def landscape():
    b = ""
    cols = [("Find", BLUE, ["XBOW", "Harness + Qwiet AI (Joern)", "Semgrep", "ZeroPath · Corgea · DryRun", "AISLE → Cohere", "Big Sleep · Codex · Claude"]),
            ("Fix", NAVY, ["Trail of Bits · Buttercup", "Theori · Xint", "Pixee", "Snyk", "Harness remediation agent"]),
            ("Secure the AI", RED, ["Lakera → Check Point", "Protect AI → Palo Alto", "HiddenLayer", "Socket", "Promptfoo → OpenAI"]),
            ("Pentest", GOLD, ["XBOW", "Horizon3", "RunSybil", "Pentera", "Bugcrowd · HackerOne"])]
    for i, (title, col, items) in enumerate(cols):
        x = 20 + i * 265
        b += f"<rect x='{x}' y='20' width='245' height='52' rx='10' fill='{col}'/>"
        b += text(x + 122, 54, title, 22, "#fff", "middle", True)
        for j, it in enumerate(items):
            b += f"<rect x='{x}' y='{90 + j * 54}' width='245' height='44' rx='8' fill='{TINT}' stroke='{LIGHT}'/>"
            b += text(x + 122, 118 + j * 54, it, 16, INK, "middle")
    b += text(540, 430, "→ = acquired, 2025–26.  Every box ships an agent, and therefore also has to defend one.", 16, GRAY, "middle")
    write("landscape.svg", svg(1080, 450, b))

if __name__ == "__main__":
    for f in (cve_growth, job_waves, aixcc, bigsleep, nondeterminism, passk, location, caro, qi2015,
              agent_loop, patch_sets, decide, pipeline, station1, network, ghidra, contract, timeline, landscape):
        f()
    print("wrote", sorted(x for x in os.listdir(HERE) if x.endswith(".svg")))
