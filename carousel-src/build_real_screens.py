#!/usr/bin/env python3
"""Phase 3 screens redrawn to match Ronas's actual Figma designs.

Built from the exported frames Max sent over (Notes tab on the athlete profile,
the athlete's note composer, the AI Analysis chat, and the video + AI analysis
view). Layout, copy and colour follow those frames; faces are replaced with
initial circles rather than inventing photos of minors.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 750, 1624
BG      = (11, 11, 13)
CARD    = (29, 29, 31)
CARD2   = (38, 38, 41)
TEAL    = (34, 211, 197)
TEAL_DK = (23, 122, 115)
TXT     = (255, 255, 255)
SUB     = (142, 142, 147)
DIM     = (108, 108, 114)
AMBER   = (200, 135, 63)
RED     = (240, 57, 94)

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

def wrap(d, text, f, maxw):
    out, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if tw(d, t, f) <= maxw: line = t
        else: out.append(line); line = word
    if line: out.append(line)
    return out

def para(d, text, f, x, y, maxw, col=TXT, lh=40):
    for ln in wrap(d, text, f, maxw):
        d.text((x, y), ln, font=f, fill=col); y += lh
    return y

def new_screen():
    im = Image.new("RGB", (W, H), BG)
    return im, ImageDraw.Draw(im)

def status_bar(d):
    d.text((44, 34), "9:41", font=F(BOLD, 26), fill=TXT)
    x = W - 150
    for i, hgt in enumerate([9, 14, 19, 24]):
        d.rounded_rectangle([x + i * 11, 52 - hgt, x + i * 11 + 7, 52], 2, fill=TXT)
    wx = x + 56
    for r in (17, 11, 4):
        d.arc([wx - r, 34 + (17 - r), wx + r, 34 + (17 - r) + 2 * r], 210, 330, fill=TXT, width=4)
    d.ellipse([wx - 3, 48, wx + 3, 54], fill=TXT)
    bx = W - 76
    d.rounded_rectangle([bx, 32, bx + 40, 54], 6, outline=TXT, width=3)
    d.rounded_rectangle([bx + 3, 35, bx + 30, 51], 4, fill=TXT)
    d.rounded_rectangle([bx + 42, 39, bx + 46, 47], 2, fill=TXT)

def back_circle(d, cx=76, cy=124, r=36):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(78, 78, 84), width=3)
    d.line([(cx + 9, cy - 15), (cx - 7, cy)], fill=TXT, width=5)
    d.line([(cx - 7, cy), (cx + 9, cy + 15)], fill=TXT, width=5)

def avatar(d, x, y, r, col, ini):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    f = F(BOLD, int(r * 0.82))
    d.text((x - tw(d, ini, f) // 2, y - th(d, ini, f) // 2 - int(r * 0.16)), ini, font=f, fill=(20, 20, 22))

def tabs(d, y, active=2, labels=("Journey", "Gallery", "Notes")):
    x0, x1 = 40, W - 40
    d.rounded_rectangle([x0, y, x1, y + 84], 42, fill=CARD)
    seg = (x1 - x0) / 3
    for i, lab in enumerate(labels):
        cx = x0 + seg * (i + 0.5)
        f = F(BOLD, 27)
        if i == active:
            pw = seg - 8
            d.rounded_rectangle([cx - pw / 2, y + 5, cx + pw / 2, y + 79], 38, fill=TXT)
            d.text((cx - tw(d, lab, f) / 2, y + 26), lab, font=f, fill=(16, 16, 18))
        else:
            d.text((cx - tw(d, lab, f) / 2, y + 26), lab, font=f, fill=TXT)
    return y + 84

def bottom_nav(d, avatar_col=(214, 150, 160), active=3):
    bw, bh = 330, 96
    x0 = (W - bw) // 2; y0 = H - 168
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 48, fill=CARD)
    cys = y0 + bh // 2
    # calendar
    cx = x0 + 62
    d.rounded_rectangle([cx - 20, cys - 19, cx + 20, cys + 19], 7, outline=SUB, width=3)
    d.line([(cx - 20, cys - 7), (cx + 20, cys - 7)], fill=SUB, width=3)
    # chat
    cx = x0 + 152
    d.rounded_rectangle([cx - 21, cys - 18, cx + 21, cys + 10], 9, outline=SUB, width=3)
    d.polygon([(cx - 8, cys + 10), (cx + 2, cys + 10), (cx - 8, cys + 22)], fill=SUB)
    # avatar
    cx = x0 + 258
    d.ellipse([cx - 30, cys - 30, cx + 30, cys + 30], fill=CARD2)
    avatar(d, cx, cys, 24, avatar_col, "")
    d.rounded_rectangle([(W - 190) // 2, H - 52, (W + 190) // 2, H - 46], 3, fill=(96, 96, 102))

def note_row(d, y, name, role, date, body, ini, col, visible=None):
    bf = F(REG, 25)
    lines = wrap(d, body, bf, W - 150)
    h = 118 + len(lines) * 36 + (40 if visible else 0)
    d.rounded_rectangle([40, y, W - 40, y + h], 22, fill=CARD)
    avatar(d, 82, y + 50, 26, col, ini)
    nf, rf = F(REG, 24), F(REG, 24)
    label = f"{name}, {role}" if role else name
    d.text((124, y + 36), label, font=nf, fill=SUB)
    df = F(REG, 23)
    d.text((W - 72 - tw(d, date, df), y + 37), date, font=df, fill=SUB)
    ty = y + 86
    for ln in lines:
        d.text((72, ty), ln, font=bf, fill=TXT); ty += 36
    if visible:
        d.text((72, ty + 6), visible, font=F(REG, 23), fill=AMBER)
    return y + h + 20


# ── 1 · athlete profile, Notes tab ───────────────────────────────────────
def profile_notes():
    im, d = new_screen(); status_bar(d)
    back_circle(d)
    ctr(d, "JAKE WILSON", F(BOLD, 34), 106)
    avatar(d, W // 2, 300, 96, (232, 193, 71), "JW")
    y = tabs(d, 420, active=2) + 34

    d.rounded_rectangle([40, y, W - 40, y + 92], 22, fill=CARD)
    f = F(BOLD, 30); s = "New note"
    tot = tw(d, s, f) + 46
    d.line([(W // 2 - tot // 2 + 14, y + 46), (W // 2 - tot // 2 + 44, y + 46)], fill=TXT, width=4)
    d.line([(W // 2 - tot // 2 + 29, y + 31), (W // 2 - tot // 2 + 29, y + 61)], fill=TXT, width=4)
    d.text((W // 2 - tot // 2 + 60, y + 30), s, font=f, fill=TXT)
    y += 118

    y = note_row(d, y, "Ethan Parker", "Head coach", "Jul 22",
                 "Showing good effort and a positive attitude in training. He listens well, "
                 "stays focused, and is starting to understand his role better. With continued "
                 "work on confidence and consistency, he has good potential to keep improving.",
                 "EP", (120, 150, 180))
    y = note_row(d, y, "Jake Wilson", None, "Jul 19",
                 "I know I still need to be more consistent in basketball. I want to improve my "
                 "ball handling, passing, and finishing at the rim, and also make better decisions "
                 "when the defense puts pressure on me.",
                 "JW", (232, 193, 71), visible="Visible to team coach")

    bottom_nav(d)
    im.save(f"{OUT}/p3_profile_notes.png"); return f"{OUT}/p3_profile_notes.png"


# ── 2 · the athlete's own note, both visibility rules on screen ──────────
def note_athlete():
    im, d = new_screen(); status_bar(d)
    d.rounded_rectangle([0, 96, W, H], 34, fill=(26, 26, 28))
    cx, cy, r = 122, 204, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(96, 96, 102), width=3)
    for a, b in (((-14, -14), (14, 14)), ((14, -14), (-14, 14))):
        d.line([(cx + a[0], cy + a[1]), (cx + b[0], cy + b[1])], fill=TXT, width=5)
    ctr(d, "NOTE", F(BOLD, 38), 182)
    cx = W - 122
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TEAL)
    d.line([(cx - 17, cy + 1), (cx - 4, cy + 15)], fill=(16, 16, 18), width=7)
    d.line([(cx - 4, cy + 15), (cx + 19, cy - 14)], fill=(16, 16, 18), width=7)

    para(d, "I feel like I've made some good progress, but I also know I still have a lot to "
            "work on. Sometimes I lose focus or get frustrated, and I want to do better with "
            "that. I'm going to keep trying to improve and trust the process.",
         F(REG, 31), 72, 290, W - 144, TXT, 48)

    y = H - 430
    d.rounded_rectangle([72, y, W - 72, y + 112], 22, fill=(46, 46, 49))
    d.text((110, y + 38), "Visible to team coach", font=F(REG, 30), fill=TXT)
    sx, sy = W - 210, y + 28
    d.rounded_rectangle([sx, sy, sx + 100, sy + 56], 28, fill=TEAL_DK)
    d.ellipse([sx + 48, sy + 4, sx + 96, sy + 52], fill=TXT)
    ctr(d, "Your notes are always visible to your parents", F(REG, 25), y + 148, SUB)
    ctr(d, "Delete note", F(BOLD, 31), y + 244, RED)

    im.save(f"{OUT}/p3_note_athlete.png"); return f"{OUT}/p3_note_athlete.png"


# ── 3 · AI Analysis, the assistant ───────────────────────────────────────
def ai_chat():
    im, d = new_screen(); status_bar(d)
    back_circle(d, cy=138)
    ctr(d, "AI ANALYSIS", F(BOLD, 34), 112)
    ctr(d, "Jake Wilson", F(REG, 26), 158, SUB)
    avatar(d, W - 80, 138, 40, (232, 193, 71), "JW")

    y = 226
    bf = F(REG, 26)
    body = ("The player is reliable, with good attendance in trainings and games and little time "
            "missed because of injury. He has stayed in the same position over the seasons, which "
            "shows consistency. Focus on building confidence and improving the small details.")
    lines = wrap(d, body, bf, W - 160)
    h = 96 + len(lines) * 38
    d.rounded_rectangle([56, y, W - 56, y + h], 22, fill=CARD)
    d.text((88, y + 26), "Overview", font=F(REG, 25), fill=SUB)
    para(d, body, bf, 88, y + 70, W - 160, TXT, 38)
    y += h + 30

    # the question — this is the screen's whole point
    q = "Can you estimate chances of being recruited for the college team?"
    qf = F(REG, 27)
    ql = wrap(d, q, qf, 400)
    qh = 52 + len(ql) * 38
    d.rounded_rectangle([W - 96 - 440, y, W - 96, y + qh], 22, fill=(24, 106, 100))
    yy = y + 26
    for ln in ql:
        d.text((W - 96 - 412, yy), ln, font=qf, fill=TXT); yy += 38
    avatar(d, W - 56, y + qh - 26, 24, (226, 168, 176), "AW")
    d.text((100, y + qh + 10), "11:32am", font=F(REG, 22), fill=DIM)
    y += qh + 52

    a = ("Based on the available stats and notes, the athlete shows some promising qualities such "
         "as regular attendance, good effort, and steady improvement. These are positive signs "
         "for college recruitment.")
    al = wrap(d, a, bf, 470)
    ah = 52 + len(al) * 38
    d.rounded_rectangle([56, y, 56 + 510, y + ah], 22, fill=CARD)
    para(d, a, bf, 88, y + 26, 470, TXT, 38)
    y += ah + 34

    # the uploaded clip
    vh = 300
    d.rounded_rectangle([W - 96 - 440, y, W - 96, y + vh], 22, fill=(24, 106, 100))
    vid = Image.new("RGB", (408, vh - 24))
    vd = ImageDraw.Draw(vid)
    for i in range(vid.height):
        t = i / vid.height
        vd.line([(0, i), (vid.width, i)], fill=(int(58 + 92 * t), int(62 + 74 * t), int(66 + 58 * t)))
    im.paste(vid, (W - 96 - 428, y + 12))
    d.ellipse([W - 316 - 34, y + vh // 2 - 34, W - 316 + 34, y + vh // 2 + 34], fill=(255, 255, 255, 230))
    d.polygon([(W - 316 - 11, y + vh // 2 - 17), (W - 316 + 18, y + vh // 2),
               (W - 316 - 11, y + vh // 2 + 17)], fill=(30, 30, 34))
    avatar(d, W - 56, y + vh - 26, 24, (226, 168, 176), "AW")
    y += vh + 46

    # composer
    by = H - 172
    d.rounded_rectangle([56, by, W - 56, by + 104], 26, fill=CARD)
    d.rounded_rectangle([84, by + 26, 136, by + 78], 14, outline=SUB, width=3)
    d.line([(110, by + 40), (110, by + 64)], fill=SUB, width=4)
    d.line([(98, by + 52), (122, by + 52)], fill=SUB, width=4)
    d.text((158, by + 34), "Ask anything or upload video", font=F(REG, 26), fill=SUB)
    d.rounded_rectangle([(W - 190) // 2, H - 52, (W + 190) // 2, H - 46], 3, fill=(96, 96, 102))

    im.save(f"{OUT}/p3_ai_chat.png"); return f"{OUT}/p3_ai_chat.png"


# ── 4 · a clip with its AI analysis ──────────────────────────────────────
def ai_video():
    im, d = new_screen(); status_bar(d)
    vx0, vy0, vw, vh = 56, 110, W - 112, 742
    vid = Image.new("RGB", (vw, vh))
    vd = ImageDraw.Draw(vid)
    for i in range(vh):
        t = i / vh
        vd.line([(0, i), (vw, i)], fill=(int(56 + 96 * t), int(60 + 78 * t), int(64 + 60 * t)))
    mask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, vw - 1, vh - 1], 26, fill=255)
    im.paste(vid, (vx0, vy0), mask)
    cx, cy = W // 2, vy0 + vh // 2
    d.ellipse([cx - 46, cy - 46, cx + 46, cy + 46], fill=(236, 236, 238))
    d.polygon([(cx - 15, cy - 24), (cx + 25, cy), (cx - 15, cy + 24)], fill=(40, 40, 44))

    y = vy0 + vh + 34
    bf = F(REG, 26)
    t1 = ("The player showed strong court awareness and consistently looked to create passing "
          "opportunities under pressure. He moved well without the ball and made several smart "
          "defensive rotations, suggesting good game intelligence for his age.")
    t2 = ("Overall, he looks like a promising youth prospect with clear upside, especially if he "
          "improves decision-making and finishes more reliably around the rim.")
    l1, l2 = wrap(d, t1, bf, W - 160), wrap(d, t2, bf, W - 160)
    ch = 104 + (len(l1) + len(l2)) * 38 + 24
    d.rounded_rectangle([56, y, W - 56, y + ch], 22, fill=CARD)
    sx, sy = 92, y + 32
    for dx, dy, s in ((0, 0, 11), (17, -9, 6)):
        d.polygon([(sx + dx, sy + dy - s), (sx + dx + s * 0.42, sy + dy - s * 0.42),
                   (sx + dx + s, sy + dy), (sx + dx + s * 0.42, sy + dy + s * 0.42),
                   (sx + dx, sy + dy + s), (sx + dx - s * 0.42, sy + dy + s * 0.42),
                   (sx + dx - s, sy + dy), (sx + dx - s * 0.42, sy + dy - s * 0.42)], fill=TXT)
    d.text((132, y + 20), "AI analysis", font=F(REG, 26), fill=SUB)
    yy = para(d, t1, bf, 92, y + 78, W - 160, TXT, 38)
    para(d, t2, bf, 92, yy + 22, W - 160, TXT, 38)

    by = H - 150
    for i, kind in enumerate(("share", "info", "spark", "trash")):
        cxx = 122 + i * 168
        fill = TEAL_DK if kind == "spark" else CARD
        d.ellipse([cxx - 46, by - 46, cxx + 46, by + 46], fill=fill)
        col = TXT if kind == "spark" else SUB
        if kind == "share":
            d.line([(cxx, by - 20), (cxx, by + 14)], fill=col, width=4)
            d.line([(cxx - 13, by - 8), (cxx, by - 21)], fill=col, width=4)
            d.line([(cxx + 13, by - 8), (cxx, by - 21)], fill=col, width=4)
            d.arc([cxx - 22, by - 6, cxx + 22, by + 26], 0, 180, fill=col, width=4)
        elif kind == "info":
            d.ellipse([cxx - 22, by - 22, cxx + 22, by + 22], outline=col, width=4)
            d.ellipse([cxx - 3, by - 14, cxx + 3, by - 8], fill=col)
            d.line([(cxx, by - 2), (cxx, by + 14)], fill=col, width=4)
        elif kind == "spark":
            for dx, dy, s in ((0, 0, 15), (20, -12, 8)):
                d.polygon([(cxx + dx, by + dy - s), (cxx + dx + s * 0.42, by + dy - s * 0.42),
                           (cxx + dx + s, by + dy), (cxx + dx + s * 0.42, by + dy + s * 0.42),
                           (cxx + dx, by + dy + s), (cxx + dx - s * 0.42, by + dy + s * 0.42),
                           (cxx + dx - s, by + dy), (cxx + dx - s * 0.42, by + dy - s * 0.42)], fill=col)
        else:
            d.rounded_rectangle([cxx - 15, by - 14, cxx + 15, by + 20], 5, outline=col, width=4)
            d.line([(cxx - 22, by - 14), (cxx + 22, by - 14)], fill=col, width=4)
            d.line([(cxx - 7, by - 22), (cxx + 7, by - 22)], fill=col, width=4)
    d.rounded_rectangle([(W - 190) // 2, H - 52, (W + 190) // 2, H - 46], 3, fill=(96, 96, 102))

    im.save(f"{OUT}/p3_ai_video.png"); return f"{OUT}/p3_ai_video.png"


for fn in (profile_notes, note_athlete, ai_chat, ai_video):
    print("built", fn())
