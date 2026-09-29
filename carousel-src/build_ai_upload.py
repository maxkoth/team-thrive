#!/usr/bin/env python3
"""Phase 3 · AI Video — the upload side, to pair with concept/ai.png.

Per the Phase 3 spec the parent is the one who uploads; the athlete can view
the feedback but not submit clips. That split is stated on the screen.
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

def header(d, title):
    cy = 118
    d.ellipse([36, cy - 26, 88, cy + 26], fill=CARD)
    d.line([(68, cy - 11), (56, cy)], fill=TXT, width=4)
    d.line([(56, cy), (68, cy + 11)], fill=TXT, width=4)
    ctr(d, title, F(BOLD, 27), cy - 16)

def bottom_nav(d, active=3):
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
            d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=CARD2)
    d.rounded_rectangle([(W - 180) // 2, H - 46, (W + 180) // 2, H - 40], 3, fill=(90, 90, 95))

def dashed_rect(d, box, r, col, seg=16, gap=12, w=3):
    x0, y0, x1, y1 = box
    def run(pts_from, pts_to, horiz):
        a, b = (pts_from, pts_to)
        x = a
        while x < b:
            x2 = min(x + seg, b)
            if horiz: d.line([(x, pts_h), (x2, pts_h)], fill=col, width=w)
            else:     d.line([(pts_h, x), (pts_h, x2)], fill=col, width=w)
            x = x2 + gap
    global pts_h
    pts_h = y0; run(x0 + r, x1 - r, True)
    pts_h = y1; run(x0 + r, x1 - r, True)
    pts_h = x0; run(y0 + r, y1 - r, False)
    pts_h = x1; run(y0 + r, y1 - r, False)
    for cx, cy, s, e in ((x0 + r, y0 + r, 180, 270), (x1 - r, y0 + r, 270, 360),
                         (x1 - r, y1 - r, 0, 90),    (x0 + r, y1 - r, 90, 180)):
        d.arc([cx - r, cy - r, cx + r, cy + r], s, e, fill=col, width=w)

def screen_ai_upload():
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    status_bar(d); header(d, "AI VIDEO")

    y = 200
    ctr(d, "Upload a clip", F(BOLD, 42), y)
    ctr(d, "Ten seconds is enough — the AI does", F(REG, 23), y + 64, SUB)
    ctr(d, "the rest before you leave the gym.", F(REG, 23), y + 98, SUB)

    # drop area
    by0, by1 = y + 156, y + 496
    dashed_rect(d, (48, by0, W - 48, by1), 28, (78, 78, 82))
    cx, cy = W // 2, (by0 + by1) // 2 - 26
    d.rounded_rectangle([cx - 62, cy - 44, cx + 62, cy + 40], 18, outline=ACCENT, width=4)
    d.polygon([(cx + 62, cy - 20), (cx + 96, cy - 42), (cx + 96, cy + 38), (cx + 62, cy + 16)],
              outline=ACCENT, width=4)
    d.ellipse([cx - 96, cy - 58, cx - 56, cy - 18], fill=BG)
    ctr(d, "Tap to record or choose", F(BOLD, 26), cy + 78)
    ctr(d, "MP4 or MOV · up to 60 seconds", F(REG, 20), cy + 116, SUB)

    y = by1 + 44
    d.rounded_rectangle([48, y, W - 48, y + 92], 24, fill=ACCENT)
    f = F(BOLD, 30)
    d.text(((W - tw(d, "Choose a clip", f)) // 2, y + 28), "Choose a clip", font=f, fill=(12, 12, 14))
    y += 136

    d.text((48, y), "WHAT HAPPENS NEXT", font=F(BOLD, 21), fill=SUB)
    y += 44
    steps = [("1", "The AI reads the technique"),
             ("2", "You get feedback in seconds"),
             ("3", "It saves to your athlete's profile")]
    for n, txt in steps:
        d.rounded_rectangle([48, y, W - 48, y + 92], 20, fill=CARD)
        d.ellipse([76, y + 24, 120, y + 68], fill=ACCENT)
        nf = F(BOLD, 25)
        d.text((98 - tw(d, n, nf) // 2, y + 32), n, font=nf, fill=(12, 12, 14))
        d.text((142, y + 32), txt, font=F(REG, 25), fill=TXT)
        y += 106

    y += 6
    ctr(d, "Parents upload clips. Athletes can view the feedback.", F(REG, 21), y, SUB)

    bottom_nav(d, active=3)
    im.save(f"{OUT}/ai_upload.png"); return f"{OUT}/ai_upload.png"

print("built", screen_ai_upload())
