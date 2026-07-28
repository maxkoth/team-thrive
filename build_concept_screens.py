#!/usr/bin/env python3
"""Concept app screens for Phase 2 & Phase 3 features, drawn in the Team Thrive app UI style."""
import os, math
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
def tw(d, s, f): return d.textbbox((0,0), s, font=f)[2]
def th(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[3]-b[1]
def ctr(d, s, f, y, col=TXT, x0=0, x1=W):
    d.text((x0 + (x1-x0-tw(d,s,f))//2, y), s, font=f, fill=col)

def new_screen():
    im = Image.new("RGB", (W, H), BG)
    return im, ImageDraw.Draw(im)

def status_bar(d):
    d.text((44, 34), "9:41", font=F(BOLD, 26), fill=TXT)
    x = W - 150
    for i, hgt in enumerate([9, 14, 19, 24]):
        d.rounded_rectangle([x+i*11, 52-hgt, x+i*11+7, 52], 2, fill=TXT)
    wx = x + 56
    for r, a in [(17, 1), (11, 1), (4, 1)]:
        d.arc([wx-r, 34+ (17-r), wx+r, 34+(17-r)+2*r], 210, 330, fill=TXT, width=4)
    d.ellipse([wx-3, 48, wx+3, 54], fill=TXT)
    bx = W - 76
    d.rounded_rectangle([bx, 32, bx+40, 54], 6, outline=TXT, width=3)
    d.rounded_rectangle([bx+3, 35, bx+30, 51], 4, fill=TXT)
    d.rounded_rectangle([bx+42, 39, bx+46, 47], 2, fill=TXT)

def header(d, title, right=None):
    cy = 118
    d.ellipse([36, cy-26, 88, cy+26], fill=CARD)
    d.line([(68, cy-11), (56, cy)], fill=TXT, width=4)
    d.line([(56, cy), (68, cy+11)], fill=TXT, width=4)
    ctr(d, title, F(BOLD, 27), cy-16)
    if right == "plus":
        d.ellipse([W-88, cy-26, W-36, cy+26], fill=ACCENT)
        d.line([(W-62, cy-12), (W-62, cy+12)], fill=(12,12,14), width=5)
        d.line([(W-74, cy), (W-50, cy)], fill=(12,12,14), width=5)
    elif right == "dots":
        for k in range(3):
            d.ellipse([W-66, cy-16+k*13, W-58, cy-8+k*13], fill=TXT)

def bottom_nav(d, active=0):
    bw, bh = 420, 84
    x0 = (W-bw)//2; y0 = H-150
    d.rounded_rectangle([x0, y0, x0+bw, y0+bh], 42, fill=(38,38,40))
    for i in range(5):
        cx = x0 + 52 + i*79; cy = y0 + bh//2
        col = TXT if i == active else DIM
        if i == 0:
            d.rounded_rectangle([cx-15, cy-14, cx+15, cy+15], 6, outline=col, width=3)
            d.line([(cx-15, cy-4), (cx+15, cy-4)], fill=col, width=3)
        elif i == 1:
            d.rounded_rectangle([cx-16, cy-13, cx+16, cy+9], 8, outline=col, width=3)
            d.polygon([(cx-6, cy+9), (cx+2, cy+9), (cx-6, cy+18)], fill=col)
        elif i == 2:
            d.ellipse([cx-14, cy-16, cx+2, cy], outline=col, width=3)
            d.arc([cx-19, cy-2, cx+7, cy+20], 180, 360, fill=col, width=3)
            d.ellipse([cx+2, cy-12, cx+15, cy+1], outline=col, width=3)
        elif i == 3:
            d.rounded_rectangle([cx-16, cy-12, cx+10, cy+12], 5, outline=col, width=3)
            d.polygon([(cx+10, cy-3), (cx+18, cy-10), (cx+18, cy+10), (cx+10, cy+3)], outline=col, width=3)
        else:
            d.ellipse([cx-16, cy-16, cx+16, cy+16], fill=(120,90,70) if i==active else CARD2)
    d.rounded_rectangle([(W-180)//2, H-46, (W+180)//2, H-40], 3, fill=(90,90,95))

def avatar(d, x, y, r, col, initials=""):
    d.ellipse([x-r, y-r, x+r, y+r], fill=col)
    if initials:
        f = F(BOLD, int(r*0.85))
        d.text((x-tw(d,initials,f)//2, y-th(d,initials,f)//2-int(r*0.16)), initials, font=f, fill=(255,255,255))

# ───────────────────────── PHASE 2 · Club ─────────────────────────
def screen_club():
    im, d = new_screen(); status_bar(d); header(d, "CLUB", right="plus")
    y = 190
    d.rounded_rectangle([28, y, W-28, y+180], 20, fill=CARD)
    avatar(d, 100, y+90, 46, (58,90,180), "EG")
    d.text((166, y+52), "ENA Gymnastics", font=F(BOLD, 32), fill=TXT)
    d.text((166, y+96), "Club · 4 teams · 86 athletes", font=F(REG, 23), fill=SUB)
    d.text((28, y+218), "TEAMS", font=F(BOLD, 21), fill=SUB)
    teams = [("Wild Wolves", "Basketball · 12 athletes", (222,168,42), "WW"),
             ("Red Hawks",   "Basketball · 14 athletes", (196,66,54), "RH"),
             ("Thunder U14", "Soccer · 18 athletes",     (64,128,214), "TU"),
             ("Lightning",   "Gymnastics · 22 athletes", (150,80,196), "LT")]
    ty = y + 254
    for name, meta, col, ini in teams:
        d.rounded_rectangle([28, ty, W-28, ty+118], 18, fill=CARD)
        avatar(d, 92, ty+59, 34, col, ini)
        d.text((150, ty+30), name, font=F(BOLD, 27), fill=TXT)
        d.text((150, ty+68), meta, font=F(REG, 22), fill=SUB)
        d.line([(W-72, ty+48), (W-58, ty+59)], fill=DIM, width=4)
        d.line([(W-58, ty+59), (W-72, ty+70)], fill=DIM, width=4)
        ty += 134
    d.rounded_rectangle([28, ty+8, W-28, ty+96], 18, outline=ACCENT, width=3)
    f = F(BOLD, 26); s = "+  Add a team"
    d.text(((W-tw(d,s,f))//2, ty+38), s, font=f, fill=ACCENT)
    ty += 148
    d.text((28, ty), "CLUB COACHES", font=F(BOLD, 21), fill=SUB)
    ty += 40
    for nm, role, col, ini in [("Ethan Parker", "Head Coach", (72,132,96), "EP"),
                               ("Caleb Johnson", "Assistant Coach", (150,96,60), "CJ"),
                               ("Maya Ortiz", "Athletic Trainer", (110,86,170), "MO")]:
        d.rounded_rectangle([28, ty, W-28, ty+104], 18, fill=CARD)
        avatar(d, 88, ty+52, 30, col, ini)
        d.text((142, ty+26), nm, font=F(BOLD, 25), fill=TXT)
        d.text((142, ty+60), role, font=F(REG, 21), fill=SUB)
        ty += 118
    bottom_nav(d, active=4)
    im.save(f"{OUT}/club.png"); return f"{OUT}/club.png"

# ───────────────────────── PHASE 2 · Invite ─────────────────────────
def screen_invite():
    im, d = new_screen(); status_bar(d); header(d, "INVITE")
    y = 200
    ctr(d, "Invite your team", F(BOLD, 40), y)
    ctr(d, "Share one link — parents and athletes", F(REG, 24), y+62, SUB)
    ctr(d, "join instantly, no manual adding.", F(REG, 24), y+96, SUB)
    bx0, by0, bx1, by1 = 90, y+160, W-90, y+460
    d.rounded_rectangle([bx0, by0, bx1, by1], 24, fill=(255,255,255))
    qx, qy, cell = bx0+62, by0+50, 20
    pat = [
        "1111111011010001111111","1000001010111010000001","1011101001010010111101",
        "1011101011001110111101","1011101000110010111101","1000001011010110000001",
        "1111111010101010111111","0000000011100100000000","1101111010011011010111",
        "0100010101101000110100","1110011011010111011011","0011101000101100101101",
        "1101011011011011010110","0100100100100100101001","1111111001011010011011",
        "1000001010110101101001","1011101001101011011010","1011101011010110100101",
        "1011101000101101011010","1000001011011010110101","1111111001101011010011",
    ]
    for r, row in enumerate(pat):
        for c, ch in enumerate(row):
            if ch == "1":
                d.rectangle([qx+c*cell, qy+r*cell, qx+c*cell+cell-2, qy+r*cell+cell-2], fill=(16,16,18))
    ly = by1 + 40
    d.rounded_rectangle([28, ly, W-28, ly+92], 18, fill=CARD)
    d.text((52, ly+18), "Invite link", font=F(REG, 20), fill=SUB)
    d.text((52, ly+46), "teamthrive.app/j/WW-4K2P", font=F(BOLD, 26), fill=ACCENT)
    d.rounded_rectangle([W-124, ly+22, W-48, ly+70], 12, fill=CARD2)
    d.rounded_rectangle([W-104, ly+36, W-78, ly+62], 5, outline=TXT, width=3)
    d.rounded_rectangle([W-94, ly+30, W-68, ly+56], 5, fill=CARD2, outline=TXT, width=3)
    by = ly + 124
    d.rounded_rectangle([28, by, W-28, by+92], 20, fill=ACCENT)
    f = F(BOLD, 29); s = "Share invite link"
    d.text(((W-tw(d,s,f))//2, by+29), s, font=f, fill=(12,12,14))
    d.rounded_rectangle([28, by+112, W-28, by+204], 20, outline=(90,90,95), width=3)
    f2 = F(BOLD, 27); s2 = "Copy link"
    d.text(((W-tw(d,s2,f2))//2, by+141), s2, font=f2, fill=TXT)
    py = by + 250
    d.text((28, py), "JOINED VIA LINK", font=F(BOLD, 21), fill=SUB)
    py += 40
    for nm, meta, col, ini in [("Amanda Wilson", "Parent of Jake · joined today", (176,86,64), "AW"),
                               ("Nina Frost", "Parent of Ella · joined today", (86,120,180), "NF"),
                               ("Dylan Parker", "Athlete · 2 days ago", (108,150,84), "DP")]:
        d.rounded_rectangle([28, py, W-28, py+104], 18, fill=CARD)
        avatar(d, 88, py+52, 30, col, ini)
        d.text((142, py+26), nm, font=F(BOLD, 25), fill=TXT)
        d.text((142, py+60), meta, font=F(REG, 20), fill=SUB)
        d.ellipse([W-84, py+40, W-60, py+64], fill=(24,60,54))
        d.line([(W-78, py+52), (W-73, py+57)], fill=ACCENT, width=3)
        d.line([(W-73, py+57), (W-65, py+47)], fill=ACCENT, width=3)
        py += 118
    im.save(f"{OUT}/invite.png"); return f"{OUT}/invite.png"

# ───────────────────────── PHASE 3 · Athlete Journey ─────────────────────────
def screen_journey():
    im, d = new_screen(); status_bar(d); header(d, "JOURNEY", right="dots")
    y = 186
    d.rounded_rectangle([28, y, W-28, y+150], 20, fill=CARD)
    avatar(d, 96, y+75, 42, (196,66,54), "JW")
    d.text((160, y+40), "Jake Wilson", font=F(BOLD, 31), fill=TXT)
    d.text((160, y+82), "3 teams · 2 sports · since 2023", font=F(REG, 22), fill=SUB)
    d.text((28, y+184), "TIMELINE", font=F(BOLD, 21), fill=SUB)
    events = [
        ("2026", "Region 7 Vault Champion", "Lightning · Gymnastics", ACCENT, True),
        ("2025", "Moved to Level 9",        "Lightning · Gymnastics", ACCENT, True),
        ("2024", "Joined Red Hawks",        "Point Guard · 42 events", (120,120,128), False),
        ("2023", "First season",            "Wild Wolves · 28 events", (120,120,128), False),
    ]
    ty = y + 224
    line_x = 62
    d.line([(line_x, ty+22), (line_x, ty+len(events)*140-40)], fill=(64,64,68), width=4)
    for yr, title, meta, col, filled in events:
        d.ellipse([line_x-14, ty+8, line_x+14, ty+36], fill=col if filled else BG,
                  outline=col, width=4)
        d.rounded_rectangle([104, ty, W-28, ty+112], 18, fill=CARD)
        d.text((130, ty+18), yr, font=F(BOLD, 20), fill=ACCENT if filled else SUB)
        d.text((130, ty+46), title, font=F(BOLD, 26), fill=TXT)
        d.text((130, ty+82), meta, font=F(REG, 21), fill=SUB)
        ty += 140
    d.rounded_rectangle([28, ty+4, W-28, ty+92], 18, fill=CARD)
    d.text((56, ty+22), "Attendance this year", font=F(REG, 22), fill=SUB)
    d.text((56, ty+50), "94%  ·  118 of 126 events", font=F(BOLD, 25), fill=ACCENT)
    ny = ty + 132
    d.text((28, ny), "NOTES", font=F(BOLD, 21), fill=SUB)
    ny += 40
    for who, txt_, col in [("Coach · Ethan Parker", "Great focus in practice this week.", ACCENT),
                           ("Parent · Amanda Wilson", "Cleared by physio, back full training.", (150,170,205))]:
        d.rounded_rectangle([28, ny, W-28, ny+108], 18, fill=CARD)
        d.text((56, ny+22), who, font=F(BOLD, 20), fill=col)
        d.text((56, ny+56), txt_, font=F(REG, 22), fill=(226,230,238))
        ny += 122
    bottom_nav(d, active=4)
    im.save(f"{OUT}/journey.png"); return f"{OUT}/journey.png"

# ───────────────────────── PHASE 3 · AI Video Feedback ─────────────────────────
def screen_ai():
    im, d = new_screen(); status_bar(d); header(d, "AI FEEDBACK")
    vy0, vy1 = 178, 566
    vw, vh = W-56, vy1-vy0
    vid = Image.new("RGB", (vw, vh))
    vd = ImageDraw.Draw(vid)
    for i in range(vh):
        t = i/vh
        vd.line([(0, i), (vw, i)], fill=(int(28+30*t), int(52+48*t), int(42+34*t)))
    vmask = Image.new("L", (vw, vh), 0)
    ImageDraw.Draw(vmask).rounded_rectangle([0, 0, vw-1, vh-1], 22, fill=255)
    im.paste(vid, (28, vy0), vmask)
    d = ImageDraw.Draw(im)
    pcx, pcy = W//2, (vy0+vy1)//2
    d.ellipse([pcx-52, pcy-52, pcx+52, pcy+52], fill=(255,255,255))
    d.polygon([(pcx-16, pcy-24), (pcx+26, pcy), (pcx-16, pcy+24)], fill=(16,16,18))
    d.rounded_rectangle([52, vy1-64, 188, vy1-24], 12, fill=(0,0,0))
    d.text((70, vy1-58), "0:18 clip", font=F(BOLD, 22), fill=TXT)
    cy = vy1 + 30
    d.rounded_rectangle([28, cy, W-28, cy+58], 14, fill=(24,60,54))
    d.text((52, cy+15), "AI ANALYSIS  ·  Developmental feedback", font=F(BOLD, 21), fill=ACCENT)
    fy = cy + 82
    d.rounded_rectangle([28, fy, W-28, fy+430], 20, fill=CARD)
    d.text((56, fy+26), "Vault — Round-off entry", font=F(BOLD, 29), fill=TXT)
    chips = [("Approach", "Strong"), ("Block", "Needs work"), ("Landing", "Good")]
    chx = 56
    for label, val in chips:
        f = F(BOLD, 19); wpx = tw(d, f"{label} · {val}", f) + 30
        col = ACCENT if val != "Needs work" else (240, 176, 72)
        d.rounded_rectangle([chx, fy+74, chx+wpx, fy+118], 22, fill=CARD2)
        d.text((chx+15, fy+87), f"{label} · {val}", font=f, fill=col)
        chx += wpx + 12
    bullets = [
        "Hurdle step is consistent and well timed.",
        "Shoulder angle opens early on block — hold",
        "the line a beat longer for more height.",
        "Chest stays tall through landing. Nice control.",
    ]
    by = fy + 148
    for i, ln in enumerate(bullets):
        if i in (0, 1, 3):
            d.ellipse([58, by+9, 70, by+21], fill=ACCENT)
        d.text((88, by), ln, font=F(REG, 23), fill=(226,230,238))
        by += 42
    d.line([(56, fy+340), (W-56, fy+340)], fill=(72,72,76), width=2)
    d.text((56, fy+362), "Saved to Jake's profile · 12 Dec 2026", font=F(REG, 21), fill=SUB)
    d.rounded_rectangle([28, fy+466, W-28, fy+558], 20, fill=ACCENT)
    f3 = F(BOLD, 28); s3 = "Upload another video"
    d.text(((W-tw(d,s3,f3))//2, fy+495), s3, font=f3, fill=(12,12,14))
    ry = fy + 598
    d.text((28, ry), "EARLIER FEEDBACK", font=F(BOLD, 21), fill=SUB)
    ry += 40
    for title_, meta in [("Bars — Kip cast", "28 Nov · 0:22 clip"),
                         ("Beam — Full turn", "14 Nov · 0:15 clip")]:
        d.rounded_rectangle([28, ry, W-28, ry+108], 18, fill=CARD)
        d.rounded_rectangle([50, ry+20, 128, ry+88], 12, fill=(38,70,58))
        d.polygon([(78, ry+40), (100, ry+54), (78, ry+68)], fill=(200,235,225))
        d.text((150, ry+26), title_, font=F(BOLD, 25), fill=TXT)
        d.text((150, ry+62), meta, font=F(REG, 21), fill=SUB)
        ry += 122
    im.save(f"{OUT}/ai.png"); return f"{OUT}/ai.png"

for fn in (screen_club, screen_invite, screen_journey, screen_ai):
    print("built", fn())
print("done")
