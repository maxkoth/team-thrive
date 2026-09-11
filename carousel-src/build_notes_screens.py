#!/usr/bin/env python3
"""Phase 3 · Notes & Journal concept screens, in the Team Thrive app UI style.

Mirrors build_concept_screens.py so these sit beside journey.png / ai.png.
The visibility rules drawn here follow the Phase 3 spec: a parent sees every
note on the child's profile, an athlete (13+) chooses per note whether the
coach sees it, and the parent can always see it either way.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 750, 1624
BG     = (16, 16, 18)
CARD   = (44, 44, 46)
CARD2  = (58, 58, 60)
ACCENT = (45, 224, 193)
TXT    = (255, 255, 255)
SUB    = (142, 142, 147)
DIM    = (99, 99, 104)
PARENT = (130, 148, 225)
ATHL   = (226, 178, 74)

FD = "/mnt/skills/examples/canvas-design/canvas-fonts"
BOLD = os.path.join(FD, "Outfit-Bold.ttf")
REG  = os.path.join(FD, "Outfit-Regular.ttf")
OUT = "concept"
os.makedirs(OUT, exist_ok=True)

def F(p, s): return ImageFont.truetype(p, s)
def tw(d, s, f): return d.textbbox((0, 0), s, font=f)[2]
def th(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[3] - b[1]
def ctr(d, s, f, y, col=TXT, x0=0, x1=W):
    d.text((x0 + (x1 - x0 - tw(d, s, f)) // 2, y), s, font=f, fill=col)

def new_screen():
    im = Image.new("RGB", (W, H), BG)
    return im, ImageDraw.Draw(im)

def status_bar(d):
    d.text((44, 34), "9:41", font=F(BOLD, 26), fill=TXT)
    x = W - 150
    for i, hgt in enumerate([9, 14, 19, 24]):
        d.rounded_rectangle([x + i * 11, 52 - hgt, x + i * 11 + 7, 52], 2, fill=TXT)
    wx = x + 56
    for r, _ in [(17, 1), (11, 1), (4, 1)]:
        d.arc([wx - r, 34 + (17 - r), wx + r, 34 + (17 - r) + 2 * r], 210, 330, fill=TXT, width=4)
    d.ellipse([wx - 3, 48, wx + 3, 54], fill=TXT)
    bx = W - 76
    d.rounded_rectangle([bx, 32, bx + 40, 54], 6, outline=TXT, width=3)
    d.rounded_rectangle([bx + 3, 35, bx + 30, 51], 4, fill=TXT)
    d.rounded_rectangle([bx + 42, 39, bx + 46, 47], 2, fill=TXT)

def header(d, title, right=None):
    cy = 118
    d.ellipse([36, cy - 26, 88, cy + 26], fill=CARD)
    d.line([(68, cy - 11), (56, cy)], fill=TXT, width=4)
    d.line([(56, cy), (68, cy + 11)], fill=TXT, width=4)
    ctr(d, title, F(BOLD, 27), cy - 16)
    if right == "plus":
        d.ellipse([W - 88, cy - 26, W - 36, cy + 26], fill=ACCENT)
        d.line([(W - 62, cy - 12), (W - 62, cy + 12)], fill=(12, 12, 14), width=5)
        d.line([(W - 74, cy), (W - 50, cy)], fill=(12, 12, 14), width=5)

def bottom_nav(d, active=0):
    bw, bh = 420, 84
    x0 = (W - bw) // 2; y0 = H - 150
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 42, fill=(38, 38, 40))
    for i in range(5):
        cx = x0 + 52 + i * 79; cy = y0 + bh // 2
        col = TXT if i == active else DIM
        if i == 0:
            d.rounded_rectangle([cx - 15, cy - 14, cx + 15, cy + 15], 6, outline=col, width=3)
            d.line([(cx - 15, cy - 4), (cx + 15, cy - 4)], fill=col, width=3)
        elif i == 1:
            d.rounded_rectangle([cx - 16, cy - 13, cx + 16, cy + 9], 8, outline=col, width=3)
            d.polygon([(cx - 6, cy + 9), (cx + 2, cy + 9), (cx - 6, cy + 18)], fill=col)
        elif i == 2:
            d.ellipse([cx - 14, cy - 16, cx + 2, cy], outline=col, width=3)
            d.arc([cx - 19, cy - 2, cx + 7, cy + 20], 180, 360, fill=col, width=3)
            d.ellipse([cx + 2, cy - 12, cx + 15, cy + 1], outline=col, width=3)
        elif i == 3:
            d.rounded_rectangle([cx - 16, cy - 12, cx + 10, cy + 12], 5, outline=col, width=3)
            d.polygon([(cx + 10, cy - 3), (cx + 18, cy - 10), (cx + 18, cy + 10), (cx + 10, cy + 3)],
                      outline=col, width=3)
        else:
            d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(120, 90, 70) if i == active else CARD2)
    d.rounded_rectangle([(W - 180) // 2, H - 46, (W + 180) // 2, H - 40], 3, fill=(90, 90, 95))

def avatar(d, x, y, r, col, initials=""):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    if initials:
        f = F(BOLD, int(r * 0.85))
        d.text((x - tw(d, initials, f) // 2, y - th(d, initials, f) // 2 - int(r * 0.16)),
               initials, font=f, fill=(255, 255, 255))

def badge(d, x_right, y, text, col):
    """Small right-aligned visibility pill."""
    f = F(BOLD, 18)
    bw = tw(d, text, f) + 26
    d.rounded_rectangle([x_right - bw, y, x_right, y + 32], 16, fill=(col[0] // 5, col[1] // 5, col[2] // 5))
    d.text((x_right - bw + 13, y + 6), text, font=f, fill=col)

def wrap(d, text, f, maxw):
    out, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if tw(d, t, f) <= maxw:
            line = t
        else:
            out.append(line); line = word
    if line: out.append(line)
    return out

def note_card(d, y, role, name, rolecol, body, vis, viscol, ini):
    """One note: who wrote it, what it says, and who can see it."""
    bf = F(REG, 23)
    lines = wrap(d, body, bf, W - 150)
    h = 96 + len(lines) * 32
    d.rounded_rectangle([28, y, W - 28, y + h], 20, fill=CARD)
    avatar(d, 68, y + 44, 24, rolecol, ini)
    d.text((106, y + 24), role, font=F(BOLD, 21), fill=rolecol)
    d.text((106 + tw(d, role, F(BOLD, 21)) + 10, y + 24), "· " + name, font=F(REG, 21), fill=SUB)
    badge(d, W - 48, y + 20, vis, viscol)
    ty = y + 68
    for ln in lines:
        d.text((106, ty), ln, font=bf, fill=TXT); ty += 32
    return y + h + 18

# ── Notes on an athlete's profile: three voices, one place ────────────────
def screen_notes():
    im, d = new_screen(); status_bar(d); header(d, "NOTES", right="plus")
    y = 188
    d.rounded_rectangle([28, y, W - 28, y + 118], 20, fill=CARD)
    avatar(d, 92, y + 59, 36, (196, 66, 54), "JW")
    d.text((150, y + 30), "Jake Wilson", font=F(BOLD, 29), fill=TXT)
    d.text((150, y + 70), "Red Hawks · Point Guard", font=F(REG, 22), fill=SUB)
    y += 152

    d.text((28, y), "THIS SEASON", font=F(BOLD, 21), fill=SUB)
    y += 40

    y = note_card(d, y, "Coach", "Ethan Parker", ACCENT,
                  "Great focus in practice this week. Ready to start at guard on Saturday.",
                  "Team", ACCENT, "EP")
    y = note_card(d, y, "Parent", "Amanda Wilson", PARENT,
                  "Cleared by the physio today — back to full training, no restrictions.",
                  "Coach can see", PARENT, "AW")
    y = note_card(d, y, "Jake", "age 14", ATHL,
                  "Nervous about the meet but my free throws felt good tonight.",
                  "Private", ATHL, "JW")
    y = note_card(d, y, "Coach", "Ethan Parker", ACCENT,
                  "Missed two trainings this month — worth checking in.",
                  "Team", ACCENT, "EP")

    y += 14
    d.text((28, y), "LAST SEASON", font=F(BOLD, 21), fill=SUB)
    y += 40
    y = note_card(d, y, "Coach", "Maya Ortiz", ACCENT,
                  "Ankle fully recovered. Cleared for contact from March.",
                  "Team", ACCENT, "MO")
    y = note_card(d, y, "Jake", "age 13", ATHL,
                  "First season on Red Hawks. Want to start next year.",
                  "Coach can see", ATHL, "JW")

    bottom_nav(d, active=1)
    im.save(f"{OUT}/notes.png"); return f"{OUT}/notes.png"

# ── Writing a note: the athlete chooses what the coach sees ───────────────
def screen_note_new():
    im, d = new_screen(); status_bar(d); header(d, "NEW NOTE")
    y = 196
    d.rounded_rectangle([28, y, W - 28, y + 660], 20, fill=CARD)
    bf = F(REG, 26)
    ty = y + 30
    for ln in wrap(d, "Vault felt solid today. Coach said my run-up is finally consistent "
                      "— want to try the full at Saturday's meet.", bf, W - 110):
        d.text((56, ty), ln, font=bf, fill=TXT); ty += 38
    d.rounded_rectangle([56, ty + 4, 59, ty + 34], 2, fill=ACCENT)  # caret
    y += 696

    d.text((28, y), "WHO CAN SEE THIS", font=F(BOLD, 21), fill=SUB)
    y += 40

    # parent — always on, shown locked
    d.rounded_rectangle([28, y, W - 28, y + 104], 20, fill=CARD)
    avatar(d, 78, y + 52, 28, PARENT, "AW")
    d.text((126, y + 26), "My parent", font=F(BOLD, 26), fill=TXT)
    d.text((126, y + 62), "Always — this can't be turned off", font=F(REG, 21), fill=SUB)
    lx, ly = W - 82, y + 40
    d.rounded_rectangle([lx - 14, ly + 6, lx + 14, ly + 30], 6, outline=SUB, width=3)
    d.arc([lx - 10, ly - 6, lx + 10, ly + 16], 180, 360, fill=SUB, width=3)
    y += 120

    # coach — the athlete's choice, shown on
    d.rounded_rectangle([28, y, W - 28, y + 104], 20, fill=CARD)
    avatar(d, 78, y + 52, 28, ACCENT, "EP")
    d.text((126, y + 26), "My coach", font=F(BOLD, 26), fill=TXT)
    d.text((126, y + 62), "You choose, note by note", font=F(REG, 21), fill=SUB)
    sx, sy = W - 132, y + 34
    d.rounded_rectangle([sx, sy, sx + 84, sy + 46], 23, fill=ACCENT)
    d.ellipse([sx + 42, sy + 4, sx + 80, sy + 42], fill=(255, 255, 255))
    y += 140

    bw = W - 56
    d.rounded_rectangle([28, y, 28 + bw, y + 92], 24, fill=ACCENT)
    f = F(BOLD, 30)
    d.text(((W - tw(d, "Save note", f)) // 2, y + 28), "Save note", font=f, fill=(12, 12, 14))
    hf = F(REG, 21)
    ctr(d, "Only you can edit or delete your own notes.", hf, y + 116, SUB)

    bottom_nav(d, active=1)
    im.save(f"{OUT}/note_new.png"); return f"{OUT}/note_new.png"

print("built", screen_notes())
print("built", screen_note_new())
