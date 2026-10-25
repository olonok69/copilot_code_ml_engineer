#!/usr/bin/env python
"""Build `presentation/Copilot_Presentation.pptx` — GitHub Copilot course deck (English).

    uv run --with python-pptx --with pillow python presentation/build_pptx_copilot.py

~40 slides, 16:9, in two sessions (1 GitHub Copilot · 2 methodology and ticket knowledge graph)
plus an appendix. Section tags (§00–§16) match TECHNICAL_GUIDE.md and SPEAKER_GUIDE.md.
Adapted from the Cursor volume's `build_pptx_cursor_en.py`: same visual system and components.

Images (optional — a missing file becomes a labelled text panel, never a crash):
  presentation/kg_graph.png            the real ticket graph (redacted screenshot)
  examples/methodology/flow.png        the 11-stage flow
  examples/subagents/agents.png        subagent vs /fleet vs cloud agent

Copilot facts come only from docs/research/COPILOT_FINDINGS_2026-10-17.md (verified 2026-10-17).

Layers: 1. visual system  2. components  3. content (one `s_*()` function per slide).
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
OUT = HERE / "Copilot_Presentation.pptx"
KG_IMAGE = HERE / "kg_graph.png"

# --------------------------------------------------------------------------- #
# 1. Visual system
# --------------------------------------------------------------------------- #

BG = "0F141A"       # slide background
PANEL = "1A212B"    # cards / panels
BORDER = "2E3948"   # panel border
CODE_BG = "0A0E13"  # code blocks
BAND = "222B38"     # quote band and highlights
TEXT = "E8EAED"     # primary text
MUTED = "9AA4B2"    # secondary text
DIM = "66707E"      # footer
ACCENT = "D97757"   # coral — Session 1 and gates
BLUE = "7AA2C7"     # Session 2
GREEN = "8CC28C"    # positive status and graph accents

UI = "Segoe UI"
MONO = "Consolas"

SLIDE_W, SLIDE_H = 13.333, 7.5
FOOTER = "GitHub Copilot · Course / Workshop"

THIN = Pt(0.75)  # normal border
THICK = Pt(1.0)  # emphasis border


def In(v):
    """Inches → EMU, accepting fractions."""
    return Emu(int(round(v * 914400)))


def R(text, size, color, bold=False, font=UI):
    """Run spec: (text, size, color, bold, font)."""
    return (text, size, color, bold, font)


# --------------------------------------------------------------------------- #
# 2. Components
# --------------------------------------------------------------------------- #


def rect(slide, x, y, w, h, fill, border=None, border_w=THIN):
    """Rectangle with no shadow. `fill=None` => transparent."""
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, In(x), In(y), In(w), In(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    if border is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = RGBColor.from_string(border)
        sh.line.width = border_w
    sh.shadow.inherit = False
    return sh


def tb(slide, x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
       sa=4, ls=1.0):
    """Text box with no margins. `paras` is a list of lists of `R(...)` runs."""
    box = slide.shapes.add_textbox(In(x), In(y), In(w), In(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(sa)
        p.space_before = Pt(0)
        p.line_spacing = ls
        for text, size, color, bold, font in runs:
            run = p.add_run()
            run.text = text
            run.font.name = font
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = RGBColor.from_string(color)
    return box


def line(slide, x, y, w, h, runs, **kw):
    """Shortcut for a single-paragraph text box."""
    return tb(slide, x, y, w, h, [runs], **kw)


# --- slide chrome ----------------------------------------------------------- #


def new_slide(prs, banded=False):
    """Background + side chrome. `banded` = top/bottom stripes (title and
    part dividers); otherwise left vertical bar (content slides)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    rect(slide, -0.1, -0.1, 13.53, SLIDE_H + 0.2, BG)
    if banded:
        rect(slide, 0, 0, SLIDE_W, 0.16, ACCENT)
        rect(slide, 0, SLIDE_H - 0.16, SLIDE_W, 0.16, ACCENT)
    else:
        rect(slide, 0, 0, 0.22, SLIDE_H, ACCENT)
    return slide


def page_number(slide, n):
    line(slide, 11.8, 7.02, 1.2, 0.35, [R(str(n), 9.5, DIM, True)], align=PP_ALIGN.RIGHT)


def chrome(prs, eyebrow, title, page):
    """Content slide: left bar, eyebrow, title, rule, and footer."""
    slide = new_slide(prs)
    line(slide, 0.7, 0.55, 11.0, 0.4, [R(eyebrow, 12, ACCENT, True)])
    line(slide, 0.68, 0.92, 12.0, 1.1, [R(title, 30, TEXT, True)])
    rect(slide, 0.72, 1.72, 1.1, 0.045, ACCENT)
    line(slide, 0.7, 7.02, 8.0, 0.35, [R(FOOTER, 9.5, DIM)])
    page_number(slide, page)
    return slide


def part_divider(prs, part, title, subtitle, chips, page):
    """Part divider: stripes, part number, large title, and index chips."""
    slide = new_slide(prs, banded=True)
    line(slide, 1.0, 1.3, 11.0, 0.5, [R(part, 16, ACCENT, True)])
    line(slide, 0.95, 1.8, 11.5, 1.2, [R(title, 44, TEXT, True)])
    rect(slide, 1.02, 2.85, 1.4, 0.05, ACCENT)
    line(slide, 1.0, 3.05, 11.3, 0.6, [R(subtitle, 15, MUTED)], ls=1.1)
    for i, text in enumerate(chips):
        x = 1.0 if i % 2 == 0 else 7.0
        y = 3.85 + 0.62 * (i // 2)
        rect(slide, x, y, 5.7, 0.52, PANEL, BORDER)
        line(slide, x + 0.25, y + 0.05, 5.3, 0.42, [R(text, 12.5, TEXT)],
             anchor=MSO_ANCHOR.MIDDLE)
    page_number(slide, page)
    return slide


# --- reusable blocks -------------------------------------------------------- #


def quote(slide, text, y=6.35):
    """Closing quote band at the foot of the slide."""
    rect(slide, 0.7, y, 11.95, 0.52, BAND, BORDER)
    rect(slide, 0.7, y, 0.09, 0.52, ACCENT)
    line(slide, 0.95, y + 0.03, 11.6, 0.46,
         [R("“ ", 13, ACCENT, True), R(text, 12.5, TEXT), R(" ”", 13, ACCENT, True)],
         anchor=MSO_ANCHOR.MIDDLE)


def panel(slide, x, y, w, h, border=BORDER, border_w=THIN, fill=PANEL):
    return rect(slide, x, y, w, h, fill, border, border_w)


def bullets(slide, x, y, w, h, items, color, size=11.5, ls=1.05):
    """List with ▸ marker in the section color."""
    paras = [[R("▸  ", size, color, True), R(t, size, TEXT)] for t in items]
    return tb(slide, x, y, w, h, paras, sa=6, ls=ls)


def card(slide, x, y, w, h, title, items, color, items_h, size=11.5):
    """Panel with colored header + bullet list."""
    panel(slide, x, y, w, h)
    line(slide, x + 0.3, y + 0.22, w - 0.5, 0.4, [R(title, 14, color, True)])
    bullets(slide, x + 0.3, y + 0.72, w - 0.55, items_h, items, color, size)


def num_card(slide, x, y, w, h, badge, title, desc, desc_h):
    """Card with square badge (number, letter, or icon) + title + description."""
    panel(slide, x, y, w, h)
    rect(slide, x + 0.22, y + 0.22, 0.5, 0.5, ACCENT)
    line(slide, x + 0.22, y + 0.24, 0.5, 0.46, [R(badge, 15, BG, True)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    line(slide, x + 0.9, y + 0.16, w - 1.05, 0.4, [R(title, 14.5, TEXT, True)])
    line(slide, x + 0.9, y + 0.5, w - 1.05, desc_h, [R(desc, 11, MUTED)], ls=1.02)


def code_block(slide, x, y, w, h, lines):
    """Code block: dark box + monospace lines.

    `lines` is a list of strings or `(text, color)` tuples — color is used
    for gray comments.
    """
    rect(slide, x, y, w, h, CODE_BG, BORDER)
    paras = []
    for item in lines:
        text, color = item if isinstance(item, tuple) else (item, TEXT)
        paras.append([R(text, 11.5, color, font=MONO)])
    tb(slide, x + 0.28, y + 0.2, w - 0.5, h - 0.35, paras, sa=2, ls=1.12)


def label(slide, x, y, w, text, color=BLUE, size=11):
    """Small label above a block."""
    return line(slide, x, y, w, 0.3, [R(text, size, color, True)])


def stack_row(slide, y, name, desc, note, x=0.7, w=7.6, h=0.48):
    """Stacked row (context anatomy): name · description · note on the right."""
    panel(slide, x, y, w, h)
    line(slide, x + 0.25, y + 0.04, 2.6, 0.4, [R(name, 11.5, BLUE, True)],
         anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 3.6, y + 0.04, 4.0, 0.4, [R(desc, 10.5, TEXT)], anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 7.35, y + 0.04, 0.85, 0.4, [R(note, 9.0, MUTED)],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def flag_row(slide, y, verdict, headline, detail):
    """Wide row with colored left tab (green = good, coral = watch out)."""
    color = GREEN if verdict else ACCENT
    panel(slide, 0.7, y, 11.95, 0.58)
    rect(slide, 0.7, y, 0.08, 0.58, color)
    line(slide, 0.95, y + 0.05, 4.6, 0.48, [R(headline, 11.5, color, True)],
         anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 5.7, y + 0.05, 6.8, 0.48, [R(detail, 11.5, TEXT)],
         anchor=MSO_ANCHOR.MIDDLE)


def step_row(slide, y, label_text, detail):
    """Real-example row: stage + what happened."""
    panel(slide, 0.7, y, 11.95, 0.48)
    rect(slide, 0.7, y, 0.08, 0.48, ACCENT)
    line(slide, 0.95, y + 0.04, 2.4, 0.4, [R(label_text, 11.5, BLUE, True)],
         anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 3.5, y + 0.04, 9.0, 0.4, [R(detail, 11, TEXT)], anchor=MSO_ANCHOR.MIDDLE)


def tool_row(slide, y, phase, tool, note, highlight=False):
    """Tool-prevalence row: phase · tool · cost."""
    if highlight:
        panel(slide, 0.7, y, 11.95, 0.5, border=ACCENT, border_w=THICK, fill=BAND)
    else:
        panel(slide, 0.7, y, 11.95, 0.5)
    line(slide, 0.95, y + 0.05, 2.9, 0.4,
         [R(phase, 11.5, ACCENT if highlight else BLUE, True)], anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 3.95, y + 0.05, 7.0, 0.4, [R(tool, 11.5, TEXT)], anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 11.1, y + 0.05, 1.4, 0.4, [R(note, 9.5, MUTED)],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def compare_row(slide, y, field, left, right):
    """Comparative table row: subagent vs Background/Cloud Agent."""
    panel(slide, 0.7, y, 11.95, 0.52)
    line(slide, 0.95, y + 0.05, 3.3, 0.42, [R(field, 11.5, TEXT, True)],
         anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 4.6, y + 0.05, 3.7, 0.42, [R(left, 11, MUTED)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    line(slide, 8.6, y + 0.05, 3.7, 0.42, [R(right, 11, MUTED)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def flow_step(slide, x, y, number, text, gate=False):
    """Step in the 11-stage flow. Coral stages are gates."""
    panel(slide, x, y, 5.85, 0.56,
          border=ACCENT if gate else BORDER, border_w=THICK if gate else THIN)
    rect(slide, x + 0.14, y + 0.11, 0.34, 0.34, ACCENT if gate else BAND)
    line(slide, x + 0.14, y + 0.11, 0.34, 0.34,
         [R(number, 11, BG if gate else TEXT, True)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    line(slide, x + 0.62, y + 0.06, 5.1, 0.46, [R(text, 11.5, TEXT)],
         anchor=MSO_ANCHOR.MIDDLE)


def summary_card(slide, x, y, number, title, desc, color):
    """Compact closing card."""
    panel(slide, x, y, 5.85, 0.85)
    rect(slide, x + 0.2, y + 0.18, 0.44, 0.44, color)
    line(slide, x + 0.2, y + 0.19, 0.44, 0.42, [R(number, 13, BG, True)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    line(slide, x + 0.8, y + 0.1, 5.0, 0.35, [R(title, 12.5, TEXT, True)])
    line(slide, x + 0.8, y + 0.43, 5.0, 0.38, [R(desc, 10, MUTED)])



def picture_or_note(slide, path, x, y, w, h, note):
    """Embed an image scaled to fit (x, y, w, h); if missing, draw a text panel instead."""
    rect(slide, x - 0.02, y - 0.02, w + 0.04, h + 0.04, None, BORDER, THICK)
    if path.exists():
        try:
            from PIL import Image
            iw, ih = Image.open(path).size
            scale = min(w / iw, h / ih)
            pw, ph = iw * scale, ih * scale
            slide.shapes.add_picture(str(path), In(x + (w - pw) / 2), In(y + (h - ph) / 2),
                                     In(pw), In(ph))
            return True
        except Exception:  # pragma: no cover - fall through to the note
            pass
    panel(slide, x, y, w, h)
    line(slide, x + 0.3, y + 0.3, w - 0.6, h - 0.6,
         [R(f"[image not found: {path.name}] ", 11, ACCENT, True), R(note, 11, MUTED)],
         anchor=MSO_ANCHOR.MIDDLE)
    return False


def grid(slide, x, y, col_w, row_h, header, rows, first_w=None, size=10.0):
    """Small matrix: header row + rows. `first_w` = width of the first column."""
    first_w = first_w or col_w
    widths = [first_w] + [col_w] * (len(header) - 1)
    cx = x
    for i, (head, wdt) in enumerate(zip(header, widths)):
        rect(slide, cx, y, wdt - 0.04, row_h, BAND, BORDER)
        line(slide, cx + 0.08, y + 0.02, wdt - 0.2, row_h - 0.04,
             [R(head, size, ACCENT if i else BLUE, True)],
             align=PP_ALIGN.LEFT if i == 0 else PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        cx += wdt
    for r, cells in enumerate(rows):
        cy = y + row_h * (r + 1) + 0.04 * (r + 1)
        cx = x
        for i, (cell, wdt) in enumerate(zip(cells, widths)):
            rect(slide, cx, cy, wdt - 0.04, row_h, PANEL, BORDER)
            if cell in ("✓", "✗", "~", "—"):
                color = {"✓": GREEN, "✗": ACCENT, "~": BLUE, "—": DIM}[cell]
                runs = [R(cell, size + 2, color, True)]
            else:
                runs = [R(cell, size, TEXT if i == 0 else MUTED, i == 0)]
            line(slide, cx + 0.08, cy + 0.02, wdt - 0.2, row_h - 0.04, runs,
                 align=PP_ALIGN.LEFT if i == 0 else PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            cx += wdt


# --------------------------------------------------------------------------- #
# 3. Content — one function per slide
# --------------------------------------------------------------------------- #

_page = {"n": 0}


def nxt():
    _page["n"] += 1
    return _page["n"]


def s_title(prs):
    nxt()
    slide = new_slide(prs, banded=True)
    line(slide, 1.0, 1.4, 11.0, 0.5,
         [R("COURSE / WORKSHOP · DEVELOPER TOOLING", 14, ACCENT, True)])
    tb(slide, 0.95, 2.0, 11.5, 2.0, [
        [R("GitHub Copilot", 60, TEXT, True)],
        [R("the same methodology, ", 26, MUTED), R("five surfaces", 26, TEXT, True)],
    ], sa=10)
    rect(slide, 1.02, 4.2, 1.4, 0.05, ACCENT)
    tb(slide, 1.0, 4.45, 11.5, 1.7, [
        [R("SESSION 1 — ", 15, ACCENT, True),
         R("Copilot: surfaces · CLI & billing · instructions · permissions · context & caching · "
           "MCP · skills · agents · hooks · automation", 13.5, MUTED)],
        [R("SESSION 2 — ", 15, BLUE, True),
         R("The methodology (tool-agnostic): gated flow · CodeGraph / Serena / GSD · "
           "transfer from Claude Code · ops (machine-sync + S3) · ticket graph (graphify)", 13.5, MUTED)],
    ], sa=8)
    line(slide, 1.0, 6.7, 11.5, 0.4,
         [R("Course volume 3 (after Claude Code and Cursor; Pi in parallel). Copilot facts "
            "verified against docs.github.com and code.visualstudio.com on 2026-10-17.", 11, DIM)])


def s_agenda(prs):
    slide = chrome(prs, "AGENDA", "One course, two sessions", nxt())

    def column(x, y0, heading, color, items, step=0.37):
        line(slide, x, y0, 5.85, 0.4, [R(heading, 14, color, True)])
        for i, text in enumerate(items):
            y = y0 + 0.45 + step * i
            panel(slide, x, y, 5.85, step - 0.06)
            line(slide, x + 0.25, y + 0.02, 5.5, step - 0.1, [R(text, 11, TEXT)],
                 anchor=MSO_ANCHOR.MIDDLE)

    column(0.7, 1.95, "SESSION 1 · GitHub Copilot", ACCENT, [
        "§00  Surfaces map + feature matrix",
        "§01  Install · auth · copilot -p · models · billing",
        "§02  Memory & instructions",
        "§03  Permissions, trust, sandbox",
        "§04  Sessions",
        "§05  Context window",
        "§06  Prompt caching (honest answer)",
        "§07  MCP",
        "§08  Skills & plugins",
        "§09  Custom agents & subagents",
        "§10  Hooks",
        "§11  Automation",
    ])
    column(6.8, 1.95, "SESSION 2 · Methodology + ticket graph", BLUE, [
        "§12  The 11-stage flow + five-check gate",
        "§13  Tool prevalence: CodeGraph · Serena · GSD",
        "§14–15  Claude Code transfer · machine sync",
        "§16  Ticket graph: graphify · kg / kg-refresh",
        "WSL demo  Skills/tools verified; gated checks stay explicit",
        "Appendix  Claude Code → Cursor → Copilot · Sources",
    ])


def s_part1(prs):
    part_divider(
        prs, "SESSION 1", "GitHub Copilot",
        "One brand, five surfaces, two VS Code engines — know which one you are talking to.",
        ["§00 · Surfaces map", "§01 · Install, auth, models, billing",
         "§02–§03 · Instructions, permissions", "§04–§06 · Sessions, context, caching",
         "§07–§09 · MCP, skills, agents", "§10–§11 · Hooks, automation"],
        nxt())


# --- §00 ------------------------------------------------------------------ #

def s_surfaces(prs):
    slide = chrome(prs, "SESSION 1 · §00 · SURFACES MAP", "“Copilot” is five different surfaces", nxt())
    cards = [
        ("›_", "Copilot CLI — copilot",
         "Terminal agent, npm @github/copilot, GA 2026-02-25. NOT the retired `gh copilot` extension."),
        ("VS", "VS Code agent",
         "Agent harnesses: Copilot (same runtime as the CLI), Local (classic agent mode), "
         "plus Claude, Codex and a Cloud target."),
        ("JB", "JetBrains agent mode",
         "Agent mode + MCP supported. Skills, custom agents, instructions, prompt files: Preview."),
        ("☁", "Copilot cloud agent",
         "Formerly “coding agent”. Issue / prompt / API → ephemeral Actions sandbox → draft PR."),
        ("✓", "Copilot code review",
         "PR reviewer on github.com and in IDEs; can be requested automatically via rulesets."),
        ("+", "Also: github.com + app",
         "Chat, Agents page (github.com/copilot/agents), Spaces; desktop Copilot app (`copilot app`)."),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.815
        y = 2.0 + 1.4 * (i // 2)
        num_card(slide, x, y, 5.835, 1.18, badge, title, desc, 0.63)
    quote(slide, "Before any “Copilot can / can't” claim, ask: which surface, and which harness?")


def s_harnesses(prs):
    slide = chrome(prs, "SESSION 1 · §00 · SURFACES MAP",
                   "VS Code has two Copilot engines", nxt())
    line(slide, 4.6, 1.95, 3.7, 0.4, [R("COPILOT HARNESS", 13, BLUE, True)],
         align=PP_ALIGN.CENTER)
    line(slide, 8.6, 1.95, 3.7, 0.4, [R("LOCAL HARNESS", 13, ACCENT, True)],
         align=PP_ALIGN.CENTER)
    rows = [
        ("Runtime", "Copilot SDK — same as the CLI (Agent Host)", "Classic agent mode (extension host)"),
        ("Config shared with CLI", "~/.copilot, .mcp.json, skills, agents", "Own chat.* settings"),
        ("Hooks", "CLI schema: .github/hooks, camelCase", "Own schema: PascalCase, hookSpecificOutput"),
        ("MCP", ".mcp.json (mcpServers) + forwarded .vscode", ".vscode/mcp.json (servers + inputs)"),
        ("Prompt files / handoffs", "✗  (convert to skills)", "✓  only here"),
        ("Nested AGENTS.md", "root + cwd", "chat.useNestedAgentsMdFiles (off)"),
    ]
    for i, (field, left, right) in enumerate(rows):
        compare_row(slide, 2.4 + 0.6 * i, field, left, right)
    quote(slide, "Pick the harness in the Session Target control — then read the docs for THAT harness.")


def s_matrix(prs):
    slide = chrome(prs, "SESSION 1 · §00 · SURFACES MAP", "Feature × surface matrix", nxt())
    header = ["Feature", "CLI", "VS Code Copilot", "VS Code Local", "JetBrains", "Cloud agent", "Code review"]
    rows = [
        ["AGENTS.md / copilot-instructions", "✓", "✓", "✓", "~", "✓", "✓"],
        [".instructions.md (applyTo)", "✓", "✓", "✓", "✓", "✓", "✓"],
        ["Prompt files", "✗", "✗", "✓", "~", "✗", "✗"],
        ["Skills", "✓", "✓", "✓", "~", "✓", "✓"],
        ["Custom agents", "✓", "✓", "✓", "~", "✓", "—"],
        ["Hooks", "✓", "✓", "✓*", "—", "✓", "—"],
        ["MCP", "✓", "✓", "✓", "✓", "✓", "~"],
    ]
    grid(slide, 0.7, 1.95, 1.45, 0.42, header, rows, first_w=3.2, size=10.5)
    line(slide, 0.7, 5.75, 11.95, 0.45, [
        R("~ ", 11, BLUE, True), R("Preview / partial (JetBrains: Preview; code review: read-only MCP tools). ", 10.5, MUTED),
        R("* ", 11, ACCENT, True), R("different hook schema. ", 10.5, MUTED),
        R("— ", 11, DIM, True), R("NOT DOCUMENTED.", 10.5, MUTED),
    ])
    quote(slide, "Full matrix with sources: docs/research/COPILOT_FINDINGS_2026-10-17.md.")


# --- §01 ------------------------------------------------------------------ #

def s_install(prs):
    slide = chrome(prs, "SESSION 1 · §01 · INSTALL AND AUTH", "Install, log in, start", nxt())
    label(slide, 0.7, 1.86, 6.0, "Install (pick one)")
    code_block(slide, 0.7, 2.2, 6.0, 2.2, [
        "npm install -g @github/copilot   # Node 22+",
        "brew install --cask copilot-cli",
        "winget install GitHub.Copilot",
        "curl -fsSL https://gh.io/copilot-install | bash",
        ("# auto-update on; COPILOT_AUTO_UPDATE=false", MUTED),
    ])
    card(slide, 7.0, 1.86, 5.65, 2.55, "Auth", [
        "copilot login  (or /login): --web-flow, --device-code, --with-token",
        "Env precedence: COPILOT_GITHUB_TOKEN > GH_TOKEN > GITHUB_TOKEN",
        "PAT = fine-grained, user-owned, “Copilot Requests” permission",
        "Actions: permissions copilot-requests: write + org policy",
    ], BLUE, 1.7, size=11)
    label(slide, 0.7, 4.6, 11.95, "First run in a repo")
    code_block(slide, 0.7, 4.95, 11.95, 1.2, [
        "cd your-project && copilot      # trust-folder prompt on first launch",
        "copilot init                     # writes .github/copilot-instructions.md",
    ])
    quote(slide, "The CLI is `copilot`. If a tutorial says `gh copilot suggest`, it is the retired extension.")


def s_headless(prs):
    slide = chrome(prs, "SESSION 1 · §01 · HEADLESS, MODELS, BILLING",
                   "copilot -p, models, and AI Credits", nxt())
    label(slide, 0.7, 1.86, 7.0, "Headless (scripts / CI)")
    code_block(slide, 0.7, 2.2, 7.0, 2.45, [
        'copilot -p "Explain ./complex.ts" -s',
        "copilot -p '…' --allow-tool='shell(git:*)' \\",
        "   --deny-tool='shell(git push)' --no-ask-user",
        "copilot -p '…' --output-format=json   # JSONL",
        "copilot -p '…' --trust-folder         # repo hooks/MCP",
        "copilot -p '…' --max-ai-credits=5     # soft cap",
    ])
    card(slide, 7.95, 1.86, 4.7, 2.8, "Models", [
        "CLI default: claude-sonnet-5.5",
        "--model / COPILOT_MODEL / /model",
        "auto: Copilot picks (10% discount on paid)",
        "--effort low…max · 1M ctx: VS Code + CLI",
    ], BLUE, 1.9, size=11)
    card(slide, 0.7, 4.85, 11.95, 1.35, "Billing: GitHub AI Credits since 2026-06-01 (1 credit = $0.01)", [
        "Pro 1,500 · Pro+ 7,000 · Max 20,000 credits/month; cost = tokens incl. cached-input and "
        "cache-write. Completions free. “Premium requests” are LEGACY.",
    ], ACCENT, 0.5, size=11)
    quote(slide, "Any slide quoting “300 premium requests” is out of date (legacy annual plans only).")


# --- §02 ------------------------------------------------------------------ #

def s_memory(prs):
    slide = chrome(prs, "SESSION 1 · §02 · MEMORY AND INSTRUCTIONS",
                   "The two-level pattern, in Copilot files", nxt())
    card(slide, 0.7, 2.0, 5.85, 3.0, "Level 1 — always loaded (small)", [
        "AGENTS.md at the root — the one file every surface reads",
        "Optional small .github/copilot-instructions.md",
        ".github/instructions/*.instructions.md with applyTo globs",
        "One-line POINTERS to everything else",
    ], ACCENT, 2.1)
    card(slide, 6.8, 2.0, 5.85, 3.0, "Level 2 — on demand (the detail)", [
        "data/changes/STATUS.md — living state per ticket",
        "PLAYBOOK.md · SHARP_EDGES.md · TEST_MAP.md",
        "<TICKET>/<TICKET>.md — self-contained ledgers",
        "@path imports (CLI) only for what MUST be eager",
    ], BLUE, 2.1)
    line(slide, 0.7, 5.2, 11.95, 0.9, [
        R("Tier 0 (machine-local): ", 12, GREEN, True),
        R("IDENTITY.md, gitignored — or ~/.copilot/copilot-instructions.md for personal, "
          "machine-only instructions. The CLI does NOT read ~/.claude/CLAUDE.md.", 12, MUTED),
    ], ls=1.08)
    quote(slide, "Same cut as in Claude Code and Cursor: pointers, not copies.")


def s_loading(prs):
    slide = chrome(prs, "SESSION 1 · §02 · MEMORY AND INSTRUCTIONS", "What loads where", nxt())
    rows = [
        (True, "CLI merges everything", "CLAUDE.md, GEMINI.md, AGENTS.md, .instructions.md, .claude/rules, "
         "copilot-instructions — at git root AND cwd"),
        (False, "Nested AGENTS.md differs", "CLI: root + cwd only · cloud agent: nearest wins · "
         "VS Code Local: setting, off by default"),
        (True, "Per-folder rules → applyTo", "Safe pattern: .instructions.md with applyTo \"subdir/**\" "
         "(+ excludeAgent: code-review | cloud-agent)"),
        (False, "Prompt files are Local-only", ".github/prompts/*.prompt.md: VS Code Local, VS, JetBrains. "
         "CLI: use skills instead"),
        (False, "Copilot Memory ≠ your ledger", "Cloud, preview, 28-day expiry. VS Code /memories and CLI "
         "/chronicle are other systems"),
    ]
    for i, (verdict, headline, detail) in enumerate(rows):
        flag_row(slide, 2.0 + 0.7 * i, verdict, headline, detail)
    quote(slide, "Memory features are a complement; data/changes/ + AGENTS.md stay the source of truth.")


# --- §03 ------------------------------------------------------------------ #

def s_permissions(prs):
    slide = chrome(prs, "SESSION 1 · §03 · PERMISSIONS", "Allow, deny — and deny wins", nxt())
    label(slide, 0.7, 1.86, 6.3, "Pattern syntax: Kind(argument)")
    code_block(slide, 0.7, 2.2, 6.3, 2.5, [
        "--allow-tool='shell(git:*)'",
        "--deny-tool='shell(git push)'",
        "--deny-tool='shell(gh pr)'",
        "--allow-tool='write(src/*.ts)'  --deny-tool='read(.env)'",
        "--allow-tool='MyMCP(tool)'      --allow-url=github.com",
        ("# deny beats allow — even with --yolo", MUTED),
    ])
    card(slide, 7.25, 1.86, 5.4, 2.85, "Where it persists", [
        "Flags: never persisted",
        "Saved approvals: ~/.copilot/permissions-config.json",
        "NO repo-level allow/deny list in the CLI",
        "permissions.* rules: managed / MDM settings only",
        "disableBypassPermissionsMode blocks --yolo",
    ], BLUE, 2.0, size=11)
    panel(slide, 0.7, 4.95, 11.95, 1.2, border=ACCENT, fill=BAND)
    line(slide, 1.0, 5.05, 11.4, 1.0, [
        R("Consequence: ", 12.5, ACCENT, True),
        R("a team-wide “never push” rule that lives in the repo must be a HOOK (§10). "
          "In VS Code a false terminal auto-approve rule only asks — it does not block; the docs "
          "point to a PreToolUse deny hook for that too.", 12, TEXT),
    ], anchor=MSO_ANCHOR.MIDDLE, ls=1.08)
    quote(slide, "Allowlists decide what runs without asking; only a hook can veto by content.")


def s_trust(prs):
    slide = chrome(prs, "SESSION 1 · §03 · TRUST AND SANDBOX",
                   "Trusted folders, sandbox, cloud guardrails", nxt())
    card(slide, 0.7, 2.0, 3.85, 3.95, "Trusted folders", [
        "Prompt on first launch",
        "Gates repo hooks, workspace MCP, plugins, repo model",
        "-p in an untrusted folder SKIPS them",
        "→ --trust-folder (one run) or GITHUB_COPILOT_PROMPT_MODE_* env",
    ], ACCENT, 3.0, size=11)
    card(slide, 4.75, 2.0, 3.85, 3.95, "Local sandbox (GA 2026-10-07)", [
        "/sandbox enable · --sandbox",
        "Seatbelt / Bubblewrap / ProcessContainer",
        "network allow/block hosts, deniedPaths",
        "credential masking per host",
        "Not repo-overridable",
    ], BLUE, 3.0, size=11)
    card(slide, 8.8, 2.0, 3.85, 3.95, "Cloud agent", [
        "All tools pre-approved; hook “ask” = deny",
        "Pushes only to its copilot/ branch",
        "Cannot mark ready, approve or merge",
        "Firewall in repo settings",
        "Humans approve workflow runs",
    ], GREEN, 3.0, size=11)
    quote(slide, "In CI the trust prompt cannot appear — so your repo hook silently does not load.")


# --- §04 ------------------------------------------------------------------ #

def s_sessions(prs):
    slide = chrome(prs, "SESSION 1 · §04 · SESSIONS", "Sessions: resume, fork, rewind, delegate", nxt())
    rows = [
        ("Resume", "copilot --continue · --resume[=ID|name] · /resume — every -p run prints its ID", "CLI"),
        ("Fork / name", "/fork (works while running) · -n NAME · /rename · /worktree", "CLI"),
        ("Roll back", "/rewind (/undo): conversation only, or conversation + files — git not required", "CLI"),
        ("Checkpoints", "One per compaction (/session checkpoints) — a SUMMARY, not a file snapshot", "CLI"),
        ("Share / steer", "/share (link, file, html, gist) · /remote on — steer from web, mobile, VS Code", "CLI"),
        ("Hand off", "/delegate or a leading & → cloud agent, branch + draft PR", "CLI→cloud"),
        ("VS Code", "Checkpoints, fork from checkpoint, Session Target picks harness or Cloud", "IDE"),
    ]
    for i, (phase, tool, note) in enumerate(rows):
        tool_row(slide, 2.0 + 0.58 * i, phase, tool, note)
    quote(slide, "A compaction checkpoint is a summary; only /rewind with files restores your tree.")


# --- §05 ------------------------------------------------------------------ #

def s_context(prs):
    slide = chrome(prs, "SESSION 1 · §05 · CONTEXT WINDOW",
                   "Context window: the resource that governs everything", nxt())
    rows = [
        ("System prompt", "Hidden — always first", "fixed"),
        ("Custom instructions", "AGENTS.md + instructions — you control this", "you decide"),
        ("System + MCP tools", "Tool schemas; deferred tool search helps", "per server"),
        ("Messages", "Files read, tool output… grows every turn", "grows"),
        ("Free space + buffer", "Auto-compaction starts ≈80%, pauses ≈95%", "watch"),
    ]
    for i, (name, desc, note) in enumerate(rows):
        stack_row(slide, 2.0 + 0.58 * i, name, desc, note)
    label(slide, 8.6, 2.01, 4.05, "The controls")
    code_block(slide, 8.6, 2.35, 4.05, 2.55, [
        "/context       # breakdown",
        "/compact [focus]",
        "/usage         # tokens, credits",
        ("# >20 KiB tool output → temp file", MUTED),
        ("# COPILOT_LARGE_OUTPUT_", MUTED),
        ("#   THRESHOLD_BYTES", MUTED),
    ])
    line(slide, 0.7, 5.05, 11.95, 0.9, [
        R("VS Code: ", 12, TEXT, True),
        R("the context-window control in the chat input shows tokens, breakdown and AI credits; "
          "#codebase runs a search, it does not dump the repo. Exact default window per model: "
          "NOT DOCUMENTED in one table.", 12, MUTED),
    ], ls=1.1)
    quote(slide, "Compactions cannot be undone — compact on purpose, with a focus.")


def s_hygiene(prs):
    slide = chrome(prs, "SESSION 1 · §05 · CONTEXT WINDOW",
                   "Context hygiene: maximum signal per token", nxt())
    cards = [
        ("1", "Small, stable instructions",
         "If you can delete it without the agent going wrong, delete it. Pointers, not copies."),
        ("2", "Rare material → skills",
         "Skills load on demand by description; instructions load always."),
        ("3", "MCP in moderation",
         "Fewer servers, disabledMcpServers, deferTools: \"auto\" for big tool sets."),
        ("4", "Subagents for research",
         "Separate context windows: noise dies outside, the summary returns."),
        ("5", "Plan → implement",
         "/plan first (enforced at the tool layer), then implement."),
        ("6", "New session per task",
         "Don't drag an unrelated transcript; /compact with a focus when you must."),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.815
        y = 2.0 + 1.46 * (i // 2)
        num_card(slide, x, y, 5.835, 1.18, badge, title, desc, 0.63)
    quote(slide, "Session 2's tool prevalence is, at bottom, context policy.")


# --- §06 ------------------------------------------------------------------ #

def s_caching(prs):
    slide = chrome(prs, "SESSION 1 · §06 · PROMPT CACHING",
                   "Caching: the honest answer — no knob, real bill", nxt())
    rows = [
        (False, "A cache_control / TTL setting",
         "Does not exist in CLI, VS Code or cloud agent — NOT DOCUMENTED anywhere"),
        (True, "Caching happens and is billed",
         "Pricing tables charge cached-input and cache-write tokens per model"),
        (True, "VS Code Cache Explorer",
         "Diagnose only: per-turn hit %, reused tokens, first divergence in the prompt"),
        (True, "Keep the prefix stable",
         "Choose model/effort/tools first; don't edit instructions mid-session"),
        (True, "Fork, don't restart",
         "Forking preserves the prompt cache; subagents for side research"),
        (False, "CLI cache view",
         "None — /usage shows tokens + credits; OTel cache attributes UNVERIFIED"),
    ]
    for i, (verdict, headline, detail) in enumerate(rows):
        flag_row(slide, 1.98 + 0.66 * i, verdict, headline, detail)
    quote(slide, "You cannot set the cache; you can stop breaking it. Mechanism demo: examples/prompt-caching/.")


# --- §07 ------------------------------------------------------------------ #

def s_mcp(prs):
    slide = chrome(prs, "SESSION 1 · §07 · MCP", "One protocol, four config files", nxt())
    rows = [
        ("CLI user", "~/.copilot/mcp-config.json — mcpServers; copilot mcp add", "user"),
        ("CLI / Copilot harness", ".mcp.json or .github/mcp.json — mcpServers, needs folder trust", "repo"),
        ("VS Code Local", ".vscode/mcp.json — servers + inputs[] (${workspaceFolder})", "repo"),
        ("Cloud agent", "Repo Settings → Copilot → MCP servers (JSON in the UI)", "GitHub"),
    ]
    for i, (phase, tool, note) in enumerate(rows):
        tool_row(slide, 1.95 + 0.58 * i, phase, tool, note)
    label(slide, 0.7, 4.38, 11.95, "CLI shape — `tools` is REQUIRED")
    code_block(slide, 0.7, 4.72, 11.95, 1.45, [
        '{ "mcpServers": {',
        '   "codegraph": {"command": "codegraph", "args": ["serve","--path",".","--mcp"], "tools": ["*"]},',
        '   "context7":  {"type": "http", "url": "https://mcp.context7.com/mcp", "tools": ["*"]} } }',
    ])
    quote(slide, "mcpServers for CLI and cloud, servers for .vscode/mcp.json — the #1 copy-paste bug.")


def s_mcp_gotchas(prs):
    slide = chrome(prs, "SESSION 1 · §07 · MCP", "MCP gotchas per surface", nxt())
    cards = [
        ("Pw", "Built-ins in the CLI",
         "github-mcp-server (read-heavy), playwright, fetch, time. Don't configure Playwright twice."),
        ("☁", "Cloud agent",
         "Tools only (no resources/prompts), no OAuth remotes, secrets as COPILOT_MCP_*. Runs them without approval."),
        ("⚙", "Binaries in the cloud",
         ".github/workflows/copilot-setup-steps.yml, one job copilot-setup-steps, on the default branch."),
        ("✓", "Code review",
         "Uses an MCP tool only if annotations.readOnlyHint: true — and only when the toggle is on."),
        ("⇄", "Migrate VS Code → CLI",
         "jq '{mcpServers: .servers}' .vscode/mcp.json > .mcp.json · ${input:} servers aren't forwarded."),
        ("Org", "Org policy",
         "Enterprise allowlist by fingerprint, fail-closed; private MCP registry available."),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.815
        y = 2.0 + 1.46 * (i // 2)
        num_card(slide, x, y, 5.835, 1.18, badge, title, desc, 0.63)
    quote(slide, "Config gives capability; instructions give judgment — a trigger map makes the agent USE it.")


# --- §08 ------------------------------------------------------------------ #

def s_skills(prs):
    slide = chrome(prs, "SESSION 1 · §08 · SKILLS AND PLUGINS",
                   "Skills: one SKILL.md, most surfaces", nxt())
    label(slide, 0.7, 1.86, 6.0, "Where Copilot looks")
    code_block(slide, 0.7, 2.2, 6.0, 2.45, [
        ".github/skills/<name>/SKILL.md   # all surfaces",
        ".claude/skills/  .agents/skills/ # also read",
        "~/.copilot/skills/  ~/.agents/skills/",
        ("# VS Code ALSO reads ~/.claude/skills/", MUTED),
        ("# the CLI does NOT — copy, symlink, or", MUTED),
        ("#   copilot skill add <dir>", MUTED),
    ])
    card(slide, 7.0, 1.86, 5.65, 2.8, "Frontmatter that survives everywhere", [
        "name = folder name, lowercase-hyphen, ≤64",
        "  (VS Code silently drops a mismatch)",
        "description ≤1024 — drives auto-selection",
        "drop trigger: — not a Copilot key",
        "Invoke: /name, or automatic by description",
    ], BLUE, 1.95, size=11)
    card(slide, 0.7, 4.85, 11.95, 1.35, "Methodology skills · visible in the live WSL Copilot session", [
        "day · evidence · preview · atlassian · kg · kg-refresh · methodology-plan · sanitise-diff",
        "Personal skill set confirmed in Copilot Customizations; see session 2 for safe behavior checks.",
    ], GREEN, 0.5, size=11)
    quote(slide, "The strongest reason for a skill is enforcement: a routine you can call leaves a trace.")


# --- §09 ------------------------------------------------------------------ #

def s_agents(prs):
    slide = chrome(prs, "SESSION 1 · §09 · CUSTOM AGENTS",
                   "Custom agents: .github/agents/*.agent.md", nxt())
    label(slide, 0.7, 1.86, 5.85, "A read-only scout")
    code_block(slide, 0.7, 2.2, 5.85, 2.55, [
        ("# .github/agents/refactor-scout.agent.md", MUTED),
        "---",
        "name: refactor-scout",
        "description: Read-only blast-radius scout",
        'tools: ["read", "search"]',
        "user-invocable: true",
        "---",
        "CodeGraph first, then Serena, then grep…",
    ])
    card(slide, 6.8, 1.86, 5.85, 2.9, "What to know", [
        "The tools list IS the enforcement; prose is not",
        "As a subagent it gets NO repo instructions unless "
        "include-custom-instructions: true (CLI)",
        "handoffs[] / agents[]: VS Code Local only",
        "CLI: --agent scout, by name, or /fleet … @scout",
        "Also read: ~/.copilot/agents, .claude/agents",
    ], BLUE, 2.0, size=11)
    card(slide, 0.7, 4.95, 11.95, 1.2, "CLI built-in agents", [
        "explore · task · general-purpose · research · rubber-duck · security-review · code-review "
        "(their documented default models disagree with the CLI default table — verify on your build)",
    ], ACCENT, 0.4, size=11)
    quote(slide, "Ready to copy: examples/subagents/ and docs/ai-agents-code-methodology/copilot/agents/.")


def s_parallel(prs):
    slide = chrome(prs, "SESSION 1 · §09 · SUBAGENTS",
                   "Subagent, /fleet, or cloud agent?", nxt())
    picture_or_note(slide, HERE.parent / "examples" / "subagents" / "agents.png",
                    0.7, 1.95, 6.2, 3.05,
                    "Diagram: subagent (isolated context, summary back) vs /fleet (parallel "
                    "subagents on one plan) vs cloud agent (own sandbox, branch, draft PR).")
    card(slide, 7.15, 1.95, 5.5, 3.05, "The three options", [
        "Subagent (task tool): own context window, summary returns",
        "/fleet: parallel subagents executing a plan; background agents can be messaged",
        "Cloud agent (/delegate, &): full async session → draft PR",
    ], BLUE, 2.1, size=11)
    panel(slide, 0.7, 5.2, 11.95, 0.95, border=ACCENT, fill=BAND)
    line(slide, 1.0, 5.25, 11.4, 0.85, [
        R("Limits: ", 12, ACCENT, True),
        R("concurrency by plan (Free 2 · Pro 4 · Max 8 · Business 16 · Enterprise 32). Max depth: "
          "the reference table says 6, the env-var table says 4 — a documentation contradiction; "
          "verify on your build.", 11.5, TEXT),
    ], anchor=MSO_ANCHOR.MIDDLE, ls=1.05)
    quote(slide, "Subagent so the noise dies outside; cloud agent when the work is long and async.")


# --- §10 ------------------------------------------------------------------ #

def s_hooks(prs):
    slide = chrome(prs, "SESSION 1 · §10 · HOOKS", "Hooks: the deterministic veto", nxt())
    card(slide, 0.7, 1.95, 5.85, 3.25, "The contract (CLI + cloud agent)", [
        ".github/hooks/*.json — {version: 1, hooks: {preToolUse: […]}}",
        "Also read: ~/.copilot/hooks, .claude/settings.json hooks",
        "stdin: {toolName, toolArgs} — toolArgs may be a JSON STRING",
        "Deny: permissionDecision \"deny\" + reason, or exit 2",
        "Crash / other non-zero → fail-CLOSED (preToolUse)",
        "TIMEOUT → fail-OPEN, every event. Keep it fast",
    ], ACCENT, 2.4, size=11)
    label(slide, 6.8, 1.86, 5.85, ".github/hooks/block-external-git.json")
    code_block(slide, 6.8, 2.2, 5.85, 3.0, [
        '{ "version": 1, "hooks": { "preToolUse": [',
        '  { "type": "command",',
        '    "matcher": "bash|powershell",',
        '    "bash": "./.github/hooks/block-external-git.sh",',
        '    "powershell": "./.github/hooks/…ps1",',
        '    "timeoutSec": 10 } ] } }',
    ])
    line(slide, 0.7, 5.4, 11.95, 0.7, [
        R("VS Code Local harness: ", 11.5, BLUE, True),
        R("different schema — PascalCase events, {tool_name, tool_input}, hookSpecificOutput. "
          "Code review hooks: NOT DOCUMENTED.", 11.5, MUTED),
    ], ls=1.05)
    quote(slide, "Instructions ask; a hook guarantees — as long as it answers before the timeout.")


def s_hook_recipe(prs):
    slide = chrome(prs, "SESSION 1 · §10 · HOOKS",
                   "The portable recipe: block push, PR, merge", nxt())
    steps = [
        ("1", "One script, both payload shapes",
         "toolArgs.command (parse if string) or tool_input.command; filter on tool name too."),
        ("2", "Match the outward commands",
         "git push · gh pr create|merge|ready · gh api …/merge · release · terraform/kubectl/helm."),
        ("3", "Answer twice, exit 2",
         "permissionDecision deny + hookSpecificOutput — exit 2 is the signal both schemas document."),
        ("4", "Never answer “allow”",
         "No-op = {} — an allow could auto-approve and skip the normal prompt."),
        ("5", "Belt and braces in the CLI",
         "--deny-tool='shell(git push)' --deny-tool='shell(gh pr)' (deny beats --yolo)."),
        ("6", "Test it — with a canary",
         "bash .github/hooks/test-block-external-git.sh: a known-deny case first."),
    ]
    for i, (badge, title, desc) in enumerate(steps):
        x = 0.7 if i % 2 == 0 else 6.815
        y = 2.0 + 1.42 * (i // 2)
        num_card(slide, x, y, 5.835, 1.15, badge, title, desc, 0.6)
    quote(slide, "/pr automerge is a first-party slash command — whether it passes preToolUse is UNVERIFIED. Test it.")


# --- §11 ------------------------------------------------------------------ #

def s_automation(prs):
    slide = chrome(prs, "SESSION 1 · §11 · AUTOMATION", "From copilot -p to agents in the cloud", nxt())
    cards = [
        ("a", "copilot -p in Actions",
         "npm i -g @github/copilot · copilot-requests: write · --trust-folder · minimal --allow-tool."),
        ("b", "Agentic Workflows",
         "github/gh-aw — GitHub's recommended path over raw copilot steps (guardrails)."),
        ("c", "Cloud agent API + Automations",
         "POST /agents/repos/{o}/{r}/tasks (preview, user tokens) · schedule/event Automations."),
        ("d", "Code review via rulesets",
         "“Automatically request Copilot code review”; reads instructions from the HEAD branch."),
    ]
    for i, (badge, title, desc) in enumerate(cards):
        x = 0.7 if i % 2 == 0 else 6.785
        y = 2.0 + 1.17 * (i // 2)
        num_card(slide, x, y, 5.865, 0.95, badge, title, desc, 0.4)
    label(slide, 0.7, 4.38, 11.95, "Copilot SDK — @github/copilot-sdk · github-copilot-sdk (pip) · Go · .NET · Java")
    code_block(slide, 0.7, 4.72, 11.95, 1.4, [
        "const client = new CopilotClient();",
        'const session = await client.createSession({ model: "auto" });',
        'const reply = await session.sendAndWait({ prompt: "Review the diff" });',
        ("// programmatic hooks: onPreToolUse returns permissionDecision", MUTED),
    ])
    quote(slide, "In CI, write the allow-list on the command line — the trust prompt will never appear.")


# --- SESSION 2 ------------------------------------------------------------- #

def s_part2(prs):
    part_divider(
        prs, "SESSION 2", "The methodology + ticket graph",
        "One practical session: workflow, tools, transfer, operations, and graph-backed project memory.",
        ["§12 · The 11-stage flow + five-check gate",
         "§13 · The method's tools",
         "§14 · Transfer: from Claude Code to Copilot",
         "§15 · Ops: machine-sync + shared record (S3)",
         "§16 · Ticket graph: graphify, kg / kg-refresh"],
        nxt())


def s_flow(prs):
    slide = chrome(prs, "SESSION 2 · §12 · THE METHODOLOGY", "The real 11-stage flow", nxt())
    picture_or_note(slide, HERE.parent / "examples" / "methodology" / "flow.png",
                    0.7, 1.95, 3.3, 4.2, "11-stage flow diagram (examples/methodology/flow.mmd).")
    steps = [
        ("1", "Orient: kg skill + history-first + status-first", False),
        ("2", "Inbound triage: is the symptom in the contract?", True),
        ("3", "Regression vs pre-existing (prove it)", True),
        ("4", "Investigate: cheap deterministic oracle", False),
        ("5", "/plan → explicit human agreement", True),
        ("6", "Implement: TDD RED → GREEN, minimal", False),
        ("7", "Verify: outbound gate × 5", True),
        ("8", "Document — each fact once", False),
        ("9", "Sanitise — added lines (sanitise-diff skill)", False),
        ("10", "Handoff: the human pushes / opens the PR (hook-enforced)", False),
        ("11", "Bot review + persist lessons", True),
    ]
    for i, (number, text, gate) in enumerate(steps):
        y = 1.95 + 0.385 * i
        panel(slide, 4.25, y, 8.4, 0.34, border=ACCENT if gate else BORDER,
              border_w=THICK if gate else THIN)
        rect(slide, 4.3, y + 0.04, 0.42, 0.26, ACCENT if gate else BAND)
        line(slide, 4.3, y + 0.04, 0.42, 0.26, [R(number, 10, BG if gate else TEXT, True)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        line(slide, 4.9, y + 0.02, 7.6, 0.3, [R(text, 11, TEXT)], anchor=MSO_ANCHOR.MIDDLE)
    quote(slide, "Autonomy is earned decision by decision. Coral = gate: a red gate means STOP, no code.")


def s_gate(prs):
    slide = chrome(prs, "SESSION 2 · §12 · THE METHODOLOGY",
                   "The outbound gate is FIVE checks", nxt())
    rows = [
        ("0 · Instrument", "Run every _diag_/_sweep_ against a KNOWN-ANSWER case first; record it"),
        ("1 · Real stage", "Reproduce through the wrapper that builds the contract, not an inner function"),
        ("2 · Member list", "Assert ids/titles, never a total — two errors can cancel exactly"),
        ("3 · Deployed image", "Re-run inside the runtime image: green tests ≠ what ships"),
        ("4 · Look at it", "Open the rendered output by eye; before/after artifacts for geometry"),
    ]
    for i, (label_text, detail) in enumerate(rows):
        step_row(slide, 2.0 + 0.6 * i, label_text, detail)
    line(slide, 0.7, 5.15, 11.95, 1.0, [
        R("Five ways a green gate proves nothing: ", 12, ACCENT, True),
        R("a broken instrument · a total that matches · a gate that couldn't fail · a canary "
          "that never applied the real perturbation · a structural check read as a semantic one.",
          11.5, MUTED),
    ], ls=1.1)
    quote(slide, "Same gate as in Claude Code and Cursor — only the agent running it changes.")


def s_prevalence(prs):
    slide = chrome(prs, "SESSION 2 · §13 · METHOD TOOLS", "Which tool the agent uses, and when", nxt())
    line(slide, 0.7, 1.9, 11.95, 0.5, [
        R("Lives in .github/instructions/01-tool-prevalence.instructions.md: ", 12, MUTED),
        R("cheap → expensive, deterministic → probabilistic.", 12, TEXT, True),
    ])
    rows = [
        ("Orient", "kg skill (ticket graph) · STATUS.md · git · gh (read)", "no inference", False),
        ("Navigate", "CodeGraph codegraph_explore (MCP) — source + paths + blast radius", "1 call", False),
        ("Refactor-check", "Serena find_referencing_symbols (MCP) — MANDATORY before rename", "precise", False),
        ("Diagnose", "Deterministic oracle: parser / validator / _diag_*.py", "no inference", False),
        ("Environment", "Cloud CLI, read-only: logs, function config, queues", "read-only", False),
        ("Contract", "Playwright (built into the CLI) against the consumer's endpoint", "reproduce", False),
        ("Only at the end", "The agent's turn — to VERIFY the fix, not to diagnose", "metered", True),
    ]
    for i, (phase, tool, note, highlight) in enumerate(rows):
        tool_row(slide, 2.45 + 0.56 * i, phase, tool, note, highlight)


def s_cg_serena(prs):
    slide = chrome(prs, "SESSION 2 · §13 · METHOD TOOLS",
                   "CodeGraph + Serena on every Copilot surface", nxt())
    grid(slide, 0.7, 1.95, 2.85, 0.56,
         ["Server", "CLI + Copilot harness", "VS Code Local", "Cloud agent"],
         [["CodeGraph", ".mcp.json stdio, --path .", ".vscode/mcp.json ${workspaceFolder}",
           "repo MCP settings + setup steps"],
          ["Serena", "uvx … serena start-mcp-server", "same", "same as CodeGraph"],
          ["Playwright", "BUILT IN — don't add", "add if needed", "default, localhost"],
          ["Context7", "http, tools [\"*\"]", "same", "firewall allow mcp.context7.com"]],
         first_w=3.35, size=10.5)
    line(slide, 0.7, 5.25, 11.95, 0.9, [
        R("CodeGraph answers “what breaks?”; Serena answers “exactly who calls THIS process()?”  ",
          12, GREEN, True),
        R("Whether --path . resolves against the session cwd is UNVERIFIED — launch from the repo "
          "root or pin an absolute path in ~/.copilot/mcp-config.json.", 11.5, MUTED),
    ], ls=1.08)
    quote(slide, "Treat codegraph_explore output as already read; never rename without Serena's check.")


def s_gsd(prs):
    slide = chrome(prs, "SESSION 2 · §13 · METHOD TOOLS",
                   "GSD: Claude Code only — the Copilot substitutes", nxt())
    card(slide, 0.7, 2.0, 5.85, 3.3, "What GSD is", [
        "Claude Code plugin: phased project management",
        "discuss → plan (gate) → execute → verify",
        "Role subagents: planner, checker, executor, verifier",
        "Versioned state in .planning/",
        "No first-party Copilot equivalent",
    ], ACCENT, 2.4)
    card(slide, 6.8, 2.0, 5.85, 3.3, "Nearest Copilot pieces", [
        "/plan, --plan, Shift+Tab — enforced at the tool layer",
        "--plan --mode autopilot · /fleet for waves",
        "Role custom agents (planner/executor/verifier)",
        "agentStop decision: block = “verify before stop”",
        "Spec Kit (github/spec-kit) — third-party-confirmed only",
        "State stays in data/changes/ ledgers",
    ], BLUE, 2.4, size=11)
    quote(slide, "Same method, without the plugin: plan mode + role agents + your own ledgers.")


def s_transfer(prs):
    slide = chrome(prs, "SESSION 2 · §14 · TRANSFER",
                   "From Claude Code to Copilot", nxt())
    card(slide, 0.7, 2.0, 5.85, 2.75, "Travels UNCHANGED (the 5 rules)", [
        "Plan → agree → implement",
        "Verify on the CONSUMER's contract",
        "Solve the general class, not one input",
        "Durable trail: why, what, how verified",
        "The human owns the external (merge, deploy)",
    ], GREEN, 1.85)
    card(slide, 6.8, 2.0, 5.85, 2.75, "What changes: the surface", [
        "CLAUDE.md → AGENTS.md + .instructions.md (CLI reads CLAUDE.md too)",
        "~/.claude/skills → .github/skills (CLI gap!)",
        "settings.json allow/deny → flags + hooks",
        "PreToolUse hooks → .github/hooks preToolUse",
        "Agent Teams → /fleet + cloud agent",
        "claude -p → copilot -p --trust-folder",
    ], BLUE, 1.85, size=11)
    card(slide, 0.7, 4.95, 11.95, 1.25,
         "Starter kit: docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md + copilot/", [
             "AGENTS.md, copilot-instructions, instructions/, skills (day, atlassian, evidence, preview, "
             "kg…), hook, read-only agent, .mcp.json, copilot-setup-steps — ready to copy",
         ], ACCENT, 0.35, size=11)
    quote(slide, "Third agent, same discipline: the methodology was never the tool.")


def s_holes(prs):
    slide = chrome(prs, "SESSION 2 · §14 · TRANSFER",
                   "New holes — and how merge stays human", nxt())
    rows = [
        (False, "CLI /pr create | auto | automerge",
         "First-party commands that can merge; hook coverage UNVERIFIED → instructions + test"),
        (False, "Code review can APPROVE (preview)",
         "Counts toward required approvals; off by default — keep it off"),
        (False, "Review reads the HEAD branch",
         "A PR can rewrite its reviewer's instructions → CODEOWNERS on .github/**"),
        (True, "preToolUse deny hook + --deny-tool",
         "Vetoes push/PR/merge by content; deny beats --yolo"),
        (True, "Cloud agent structural limits",
         "copilot/ branch only; cannot approve, mark ready or merge"),
        (True, "disableBypassPermissionsMode",
         "Managed/user setting that blocks --yolo / allow-all"),
    ]
    for i, (verdict, headline, detail) in enumerate(rows):
        flag_row(slide, 1.98 + 0.66 * i, verdict, headline, detail)
    quote(slide, "In 2025 “no merge by the agent” was a policy. In 2026 it is a hook, a flag and a branch rule.")


def s_ops(prs):
    slide = chrome(prs, "SESSION 2 · §15 · OPS",
                   "From transporting (tarball) to sharing (S3)", nxt())
    card(slide, 0.7, 2.0, 5.85, 2.55, "A · Bring-up: tarball + USB", [
        "Outbound = full copy; inbound = data/ delta only",
        "Carry ~/.copilot deliberately: skills, agents, mcp-config",
        "On the target: bootstrap + target-setup.sh",
        "Re-pin the CodeGraph --path in .mcp.json",
    ], BLUE, 1.65, size=11)
    card(slide, 6.8, 2.0, 5.85, 2.55, "B · Day to day: S3-backed record", [
        "Scope grows in reviewed phases",
        "Write via sync; read via READ-ONLY mount",
        "Dry-run by default; guard BOTH directions",
        "ONE publisher; “derived” is per file",
    ], GREEN, 1.65, size=11)
    card(slide, 0.7, 4.7, 11.95, 1.5, "Agent-specific: the machine has a role", [
        "IDENTITY.md (gitignored) declares publisher | contributor; AGENTS.md points to it",
        "day skill = start/end routine; optional sessionStart prompt hook runs /day start (CLI)",
    ], ACCENT, 0.55, size=11)
    quote(slide, "A rule in a runbook decays silently; a routine you call leaves a trace.")


# --- SESSION 2 · GRAPH CASE STUDY ----------------------------------------- #

def s_part3(prs):
    part_divider(
        prs, "SESSION 2 · CONTINUED", "The ticket knowledge graph",
        "The graph is the case study inside this session—not a separate session.",
        ["§16a · Problem and pipeline",
         "§16b · The real graph, visualized",
         "§16c · Usage under Copilot (kg / kg-refresh)",
         "Appendix · Equivalences and sources"],
        nxt())


def s_kg_pipeline(prs):
    slide = chrome(prs, "SESSION 2 · §16A · TICKET GRAPH",
                   "The problem, and the pipeline", nxt())
    card(slide, 0.7, 2.0, 5.85, 2.45, "The problem", [
        "Hundreds of writeups, sharp edges, runbooks",
        "A “new” bug almost always has prior context",
        "Finding it by hand = remembering + grep",
        "The graph makes it explicit, in 1 call",
    ], ACCENT, 1.55, size=11)
    label(slide, 6.8, 1.91, 5.85, "Build (kg-refresh skill)")
    code_block(slide, 6.8, 2.25, 5.85, 2.2, [
        "kg_refresh.sh prepare   # manifest → stage",
        "                        # → scratch OUTSIDE repo",
        ("# semantic extraction: the agent step", MUTED),
        ("#   (CLI subagents: task / /fleet)", MUTED),
        "kg_refresh.sh finalize  # output/ + leak-check",
    ])
    panel(slide, 0.7, 4.65, 11.95, 1.45)
    tb(slide, 1.0, 4.78, 11.4, 1.2, [
        [R("graphify, not CodeGraph:  ", 12, GREEN, True),
         R("same role (a queryable graph before touching anything), different domain — tickets, "
           "not code.", 11.5, TEXT)],
        [R("The gotcha:  ", 12, ACCENT, True),
         R("graphify honors .gitignore and data/ is ignored → stage the corpus outside the repo, "
           "copy artifacts back. The bookends are deterministic and tested.", 11.5, TEXT)],
    ], sa=8, ls=1.1)
    quote(slide, "Every staged file keeps its provenance in its name — every node traces to a source.")


def s_kg_graph(prs):
    slide = chrome(prs, "SESSION 2 · §16B · TICKET GRAPH",
                   "The current graph: 3,921 nodes, 178 communities", nxt())
    picture_or_note(slide, KG_IMAGE, 0.7, 1.95, 8.8, 4.95,
                    "Current graph topology only; node labels and metadata omitted.")
    card(slide, 9.7, 1.95, 2.95, 3.4, "The real output", [
        "3,921 nodes · 8,508 links",
        "178 communities · 73 hyperedges",
        "94.3% EXTRACTED links",
        "5.6% INFERRED · <0.1% AMBIGUOUS",
        "310 source files",
    ], GREEN, 2.5, size=11)
    tb(slide, 9.7, 5.5, 2.95, 0.8, [
        [R("Privacy-safe visual.", 11, BLUE, True)],
        [R("The current graph contains internal labels; only its unlabeled topology is shown.",
           9.5, MUTED)],
    ], ls=1.05)


def s_kg_usage(prs):
    slide = chrome(prs, "SESSION 2 · §16C · TICKET GRAPH",
                   "Using it from Copilot", nxt())
    label(slide, 0.7, 1.91, 6.35, "Query: ZERO LLM (reads graph.json)")
    code_block(slide, 0.7, 2.25, 6.35, 1.9, [
        "kg_query.sh explain <ticket|topic>",
        "kg_query.sh path <A> <B>",
        "kg_query.sh find <substr>",
        ("# or just: /kg explain <topic>", MUTED),
    ])
    card(slide, 7.35, 1.92, 5.3, 2.25, "Where it hooks in", [
        "Stage 1 (Orient) of the flow",
        "00-methodology-core.instructions.md: kg BEFORE grep",
        "Points to WHAT to read; doesn't replace reading",
    ], ACCENT, 1.4, size=11)
    card(slide, 0.7, 4.35, 11.95, 1.8, "kg / kg-refresh under Copilot", [
        "Skills in .github/skills/ (repo) or ~/.copilot/skills/ — the CLI won't find ~/.claude/skills",
        "kg-refresh semantic step: CLI subagents (task, /fleet) — or keep running it from Claude Code",
        "Publisher-only guard lives in the script, not in the prompt · not for the cloud agent (no corpus)",
    ], BLUE, 1.0, size=11)
    quote(slide, "One semantic step at build time, zero LLM at query time.")


def s_replication(prs):
    slide = chrome(prs, "SESSION 2 · WSL PARITY CHECK",
                   "What the ILS_2 Copilot check proves—and what it doesn't", nxt())
    card(slide, 0.7, 1.95, 5.85, 3.5, "Verified safely · 2026-10-25", [
        "Course-repo Copilot session: 8 personal skills visible",
        "Course-repo MCP view: CodeGraph + Context7 connected (user-confirmed)",
        "CodeGraph CLI + bounded MCP query on the target repo",
        "Evidence: 22 offline tests · Atlassian: 62 mocked tests",
        "Synthetic methodology-plan and disposable sanitise-diff exercises",
        "Personal instructions and local MCP; no shared .github changes",
    ], GREEN, 2.65, size=10.5)
    card(slide, 6.8, 1.95, 5.85, 3.5, "Gated · not claimed as parity", [
        "Real preview: designated fixture unavailable; run not performed",
        "Evidence fetch and authenticated Atlassian reads: not run",
        "day / kg-refresh: safety gates checked; shared operations not run",
        "Serena unavailable; Pylance provided local Python navigation",
        "Skill discovery is not the same as remote end-to-end behavior",
    ], ACCENT, 2.65, size=10.5)
    line(slide, 0.7, 5.65, 11.95, 0.55, [
        R("Scope note: ", 11.5, BLUE, True),
        R("user confirmed the active course-repo customization view; target-repo results are reported "
          "separately. Source report stays local under ILS_2/data.", 11, MUTED),
    ])
    quote(slide, "Show what passed, name what was gated, and never call an unsafe shortcut a parity test.")


def s_equiv(prs):
    slide = chrome(prs, "APPENDIX", "Claude Code → Cursor → Copilot", nxt())
    grid(slide, 0.7, 1.9, 3.15, 0.4, ["Concept", "Claude Code", "Cursor", "GitHub Copilot"], [
        ["Headless", "claude -p", "agent -p --trust", "copilot -p --trust-folder"],
        ["Always-on memory", "CLAUDE.md", "AGENTS.md + rules", "AGENTS.md + instructions"],
        ["Scoped rules", ".claude/rules paths:", ".mdc globs", ".instructions.md applyTo"],
        ["Skills", "~/.claude/skills", ".cursor/skills", ".github/skills · ~/.copilot/skills"],
        ["Subagents", ".claude/agents", ".cursor/agents", ".github/agents/*.agent.md"],
        ["Parallel", "Agent Teams", "Cloud Agents", "/fleet · cloud agent"],
        ["Hooks", "settings.json", ".cursor/hooks.json", ".github/hooks/*.json"],
        ["Block a command", "exit 2 / deny", "permission deny", "permissionDecision deny / exit 2"],
        ["MCP config", ".mcp.json", ".cursor/mcp.json", ".mcp.json · .vscode/mcp.json"],
        ["PR review bot", "—", "Bugbot", "Copilot code review"],
    ], first_w=2.5, size=9.5)


def s_close(prs):
    slide = chrome(prs, "CLOSE", "From assistant to system, on any surface", nxt())
    line(slide, 0.7, 1.95, 5.85, 0.4, [R("SESSION 1 · the tool", 13, ACCENT, True)])
    left = [
        ("1", "Know the surface", "CLI ≠ gh copilot; two VS Code engines; cloud agent; review."),
        ("2", "Instructions + context", "AGENTS.md everywhere; lean, stable prefix; no cache knob."),
        ("3", "MCP + skills + agents", "mcpServers vs servers; name = folder; tools list = enforcement."),
        ("4", "Hooks + automation", "Deny + exit 2; timeouts fail open; --trust-folder in CI."),
    ]
    for i, (number, title, desc) in enumerate(left):
        summary_card(slide, 0.7, 2.35 + 0.95 * i, number, title, desc, ACCENT)
    line(slide, 6.8, 1.95, 5.85, 0.4, [R("SESSION 2 · the method and the graph", 13, BLUE, True)])
    right = [
        ("5", "The 11-stage flow", "Deterministic gates; five-check outbound gate."),
        ("6", "The method's tools", "CodeGraph · Serena · oracles; GSD → plan mode + /fleet."),
        ("7", "Transferable, enforceable", "COPILOT_ADAPTATION.md; human-owns-merge via hook."),
        ("8", "The ticket graph", "graphify: history-first, zero LLM at query time."),
    ]
    for i, (number, title, desc) in enumerate(right):
        summary_card(slide, 6.8, 2.35 + 0.95 * i, number, title, desc, BLUE)
    line(slide, 0.7, 6.3, 12.0, 0.6, [
        R("Sources (verified 2026-10-17 — Copilot moves fast, re-check before reuse):  "
          "docs.github.com/en/copilot  ·  code.visualstudio.com/docs  ·  github.blog/changelog  ·  "
          "github.com/colbymchenry/codegraph  ·  github.com/oraios/serena", 10.5, DIM)])


SLIDES = [
    s_title, s_agenda, s_part1,
    s_surfaces, s_harnesses, s_matrix,
    s_install, s_headless,
    s_memory, s_loading,
    s_permissions, s_trust,
    s_sessions,
    s_context, s_hygiene,
    s_caching,
    s_mcp, s_mcp_gotchas,
    s_skills,
    s_agents, s_parallel,
    s_hooks, s_hook_recipe,
    s_automation,
    s_part2, s_flow, s_gate, s_prevalence, s_cg_serena, s_gsd, s_transfer, s_holes, s_ops,
    s_part3, s_kg_pipeline, s_kg_graph, s_kg_usage, s_replication,
    s_equiv, s_close,
]


def build():
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    for make in SLIDES:
        make(prs)
    prs.save(str(OUT))
    return len(SLIDES)


if __name__ == "__main__":
    n = build()
    print(f"OK  {OUT}  ({n} slides)")
