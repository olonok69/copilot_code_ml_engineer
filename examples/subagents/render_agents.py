#!/usr/bin/env python3
"""
Renders agents.png — Copilot subagents vs the Copilot cloud agent — in the deck's style.
Offline, Pillow only (like ../methodology/render_flow.py).

    pip install pillow
    python render_agents.py      # -> agents.png

The editable conceptual source is agents.mmd; if you change the architecture, update both.
"""
from PIL import Image, ImageDraw, ImageFont

SS = 2
BG     = (15, 20, 26)
PANEL  = (26, 33, 43)
PANEL2 = (34, 43, 56)
STROKE = (46, 57, 72)
CORAL  = (217, 119, 87)
BLUE   = (122, 162, 199)
GREEN  = (140, 194, 140)
TEXT   = (232, 234, 237)
MUTED  = (154, 164, 178)

W, H = 1560, 760
img = Image.new("RGB", (W * SS, H * SS), BG)
d = ImageDraw.Draw(img)


def font(size, bold=False):
    import os
    windir = os.environ.get("WINDIR", r"C:\Windows")
    candidates = (
        ["DejaVuSans-Bold.ttf", os.path.join(windir, "Fonts", "seguisb.ttf"),
         os.path.join(windir, "Fonts", "arialbd.ttf")]
        if bold else
        ["DejaVuSans.ttf", os.path.join(windir, "Fonts", "segoeui.ttf"),
         os.path.join(windir, "Fonts", "arial.ttf")]
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size * SS)
        except OSError:
            continue
    return ImageFont.load_default()


def rr(x, y, w, h, r=14, fill=PANEL, outline=STROKE, width=1):
    d.rounded_rectangle([x*SS, y*SS, (x+w)*SS, (y+h)*SS], radius=r*SS,
                        fill=fill, outline=outline, width=width*SS)


def ctext(cx, cy, txt, fnt, fill=TEXT):
    b = d.textbbox((0, 0), txt, font=fnt)
    d.text((cx*SS - (b[2]-b[0])/2, cy*SS - (b[3]-b[1])/2 - b[1]), txt, font=fnt, fill=fill)


def ltext(x, y, txt, fnt, fill=TEXT):
    d.text((x*SS, y*SS), txt, font=fnt, fill=fill)


def arrow(x1, y1, x2, y2, color=MUTED, width=2, both=False):
    d.line([x1*SS, y1*SS, x2*SS, y2*SS], fill=color, width=width*SS)
    import math
    ang = math.atan2(y2-y1, x2-x1)
    for (tx, ty, a) in ([(x2, y2, ang)] + ([(x1, y1, ang + math.pi)] if both else [])):
        p = [(tx*SS, ty*SS)]
        for da in (2.6, -2.6):
            p.append(((tx - 12*math.cos(a+da*0.5))*SS, (ty - 12*math.sin(a+da*0.5))*SS))
        d.polygon(p, fill=color)


f_t  = font(24, True)
f_h  = font(17, True)
f_b  = font(14, True)
f_s  = font(12)
f_xs = font(11)

ltext(40, 28, "Copilot subagents vs. the Copilot cloud agent", f_t, TEXT)
ltext(40, 66, "Subagents: isolated context, a summary returns.  Cloud agent: a full async session on its own branch.", f_s, MUTED)

# ---------------- left panel: SUBAGENTS ----------------
rr(40, 110, 700, 560, r=18, fill=(20, 26, 34), outline=STROKE)
ltext(66, 130, "SUBAGENTS — task tool · /fleet", f_h, BLUE)
ltext(66, 160, "low cost · the expensive part dies with the subagent", f_xs, MUTED)

rr(80, 210, 240, 170, fill=PANEL2, outline=BLUE, width=2)
ctext(200, 250, "Main session", f_b, TEXT)
ctext(200, 280, "your context", f_s, MUTED)
ctext(200, 305, "(stays clean)", f_s, MUTED)

subs = [("explore (built-in)", "read-only · fast"), ("/fleet workers", "parallel plan steps"),
        ("custom .agent.md", "refactor-scout · security-reviewer")]
for i, (t, sub) in enumerate(subs):
    y = 200 + i * 150
    rr(430, y, 280, 100, fill=PANEL, outline=STROKE)
    ctext(570, y + 32, t, f_b, TEXT)
    ctext(570, y + 62, sub, f_xs, MUTED)
    arrow(320, 270, 430, y + 35, color=MUTED)
    arrow(430, y + 72, 322, 320, color=GREEN)
ltext(340, 190, "prompt with context", f_xs, MUTED)
ltext(90, 400, "only the SUMMARY returns", f_xs, GREEN)
ltext(66, 610, "Concurrency is plan-based (Free 2 ... Enterprise 32). Max depth: 6 (table) vs 4 (env row).", f_xs, MUTED)
ltext(66, 632, "Custom agents as subagents get NO repo instructions unless include-custom-instructions.", f_xs, CORAL)

# ---------------- right panel: CLOUD AGENT ----------------
rr(790, 110, 730, 560, r=18, fill=(20, 26, 34), outline=STROKE)
ltext(816, 130, "COPILOT CLOUD AGENT — delegation", f_h, CORAL)
ltext(816, 160, "/delegate · & prefix · assign an issue · @copilot on a PR · tasks API", f_xs, MUTED)

rr(850, 205, 280, 90, fill=PANEL2, outline=CORAL, width=2)
ctext(990, 235, "Delegate", f_b, TEXT)
ctext(990, 265, "from CLI / VS Code / github.com", f_xs, MUTED)
rr(1190, 205, 290, 90, fill=PANEL, outline=STROKE)
ctext(1335, 235, "Cloud agent", f_b, TEXT)
ctext(1335, 265, "full session · Actions sandbox", f_xs, MUTED)
arrow(1130, 250, 1190, 250, color=MUTED)

rr(1190, 380, 290, 90, fill=PANEL, outline=STROKE)
ctext(1335, 410, "copilot/ branch + draft PR", f_b, TEXT)
ctext(1335, 440, "pushes only there; signed, co-authored", f_xs, MUTED)
arrow(1335, 295, 1335, 380, color=MUTED)

rr(850, 380, 280, 90, fill=PANEL2, outline=GREEN, width=2)
ctext(990, 410, "Human", f_b, GREEN)
ctext(990, 440, "approves workflows · reviews · merges", f_xs, MUTED)
arrow(1190, 425, 1130, 425, color=GREEN)

ltext(816, 510, "Cannot mark ready, approve or merge. The requester cannot approve its PR.", f_xs, TEXT)
ltext(816, 535, "All tools pre-approved inside the sandbox; a hook 'ask' is treated as 'deny'.", f_xs, TEXT)
ltext(816, 560, "Its result lands as a PR, not in your context: partition the work by branch/file first.", f_xs, CORAL)

ltext(40, 706, "Side-quests -> subagents. Parallel plan -> /fleet. Long async work -> cloud agent. The human merges.", f_s, GREEN)

img = img.resize((W, H), Image.LANCZOS)
img.save("agents.png")
print(f"OK -> agents.png  ({W}x{H})")
