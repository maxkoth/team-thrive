#!/usr/bin/env python3
"""
Master post generator — all 10 posts, poster-matched color palette:
  DARK  = near-black (matches poster background)
  AQUA  = cyan-teal  (matches poster accent color)
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

FONTS = "/tmp/fonts"
IMGS  = "/tmp/deck_imgs"
OUT   = "/home/user/team-thrive/instagram"
W = H = 1080

# ── Palette (matched to Aliza's poster) ──────────────────────────────────────
DARK    = (8,   8,  18)    # near-black background
DARK2   = (18, 22,  42)    # card / row fills
DARK3   = (28, 32,  58)    # subtle highlights
AQUA    = (0,  205, 168)   # poster cyan-teal
WHITE   = (255, 255, 255)
GRAY    = (150, 165, 190)
SALMON  = (255, 100,  90)
DARK_BG_SPLIT_L = (22,  8,  22)   # before-side (dark purple-black)
DARK_BG_SPLIT_R = (6,  24,  22)   # after-side  (dark teal-black)

def f(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

def brand(draw, x=54, y=48):
    draw.text((x, y), "TEAM ", font=f("Barlow-Regular.ttf", 28), fill=WHITE)
    w = draw.textlength("TEAM ", font=f("Barlow-Regular.ttf", 28))
    draw.text((x+w, y), "THRIVE", font=f("Barlow-Bold.ttf", 28), fill=AQUA)

def rr(draw, xy, r=10, fill=None, outline=None, ow=2):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=ow)

def cta(draw, text, y, x=54, w=972, h=88, fill=AQUA, fg=DARK):
    rr(draw, [x, y, x+w, y+h], r=16, fill=fill)
    ft = f("Barlow-Bold.ttf", 34)
    tw = draw.textlength(text, font=ft)
    draw.text((x+(w-tw)/2, y+(h-34)/2-1), text, font=ft, fill=fg)

def paste_cut(base, path, w=None, h=None, pos=(0,0), anchor="tl"):
    src = Image.open(path).convert("RGBA")
    sw, sh = src.size
    if w:   src = src.resize((w, int(sh*(w/sw))), Image.LANCZOS)
    elif h: src = src.resize((int(sw*(h/sh)), h), Image.LANCZOS)
    fw, fh = src.size
    x, y = pos
    if anchor == "br": x, y = x-fw, y-fh
    elif anchor == "tr": x, y = x-fw, y
    base.paste(src, (x, y), src)
    return fw, fh

def stars(draw, cx, cy, n=3, size=8, color=None):
    color = color or AQUA
    gap = size * 3
    start = cx - gap * (n-1) / 2
    for i in range(n):
        sx = int(start + i*gap)
        draw.polygon([(sx, cy-size),(sx+size//3, cy-size//3),
                       (sx+size, cy-size//3),(sx+size//2, cy+size//4),
                       (sx+size*2//3, cy+size),(sx, cy+size//2),
                       (sx-size*2//3, cy+size),(sx-size//2, cy+size//4),
                       (sx-size, cy-size//3),(sx-size//3, cy-size//3)],
                     fill=color)

def teal_stripe(draw, y, alpha_start=120):
    """Horizontal teal glow stripe."""
    for i in range(6):
        a = int(alpha_start * (1 - i/6))
        draw.rectangle([0, y+i, W, y+i+1], fill=(*AQUA, a))


# ─── POST 1 — Sound familiar? ─────────────────────────────────────────────────
def post1():
    img = Image.new("RGB", (W,H), DARK)
    draw = ImageDraw.Draw(img)
    for i in range(12):
        off = 40 + i*22
        draw.line([(W-off, 0), (W, off)], fill=(*AQUA, 40), width=2)
    brand(draw)
    draw.text((54, 110), "Sound familiar?", font=f("Barlow-Bold.ttf", 86), fill=WHITE)
    draw.rectangle([54, 208, 200, 214], fill=AQUA)
    rows = ["4 unread texts in the team group chat",
            "2 emails from the club — still unopened",
            "Still don't know what time practice starts",
            "Coach updated the schedule... somewhere",
            "Payment reminder sitting in 3 different apps"]
    y = 232
    for row in rows:
        rr(draw, [54, y, 1026, y+76], r=10, fill=DARK2)
        draw.rectangle([54, y, 62, y+76], fill=AQUA)
        draw.text((80, y+22), row, font=f("Barlow-Regular.ttf", 27), fill=WHITE)
        y += 86
    y += 14
    draw.rectangle([54, y, 1026, y+4], fill=AQUA)
    y += 18
    draw.text((54, y), "Team Thrive puts it all in one place.",
              font=f("Barlow-Bold.ttf", 34), fill=WHITE)
    y += 54
    chips = ["Schedules","Payments","Updates","Recruiting"]
    cx = 54
    fc = f("Barlow-SemiBold.ttf", 26)
    for chip in chips:
        cw = int(draw.textlength(chip, font=fc)) + 30
        rr(draw, [cx, y, cx+cw, y+44], r=22, outline=AQUA)
        draw.text((cx+15, y+9), chip, font=fc, fill=AQUA)
        cx += cw + 14
    y += 68
    cta(draw, "Free to join  —  link in bio", y)
    draw.text((54, 1046), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)
    img.save(f"{OUT}/post1_chaos.jpg", "JPEG", quality=95)
    print("post1 ✓")


# ─── POST 2 — They work harder ────────────────────────────────────────────────
def post2():
    img = Image.new("RGB", (W,H), DARK)
    draw = ImageDraw.Draw(img)
    paste_cut(img, "/tmp/athlete_nobg.png", h=880, pos=(W,H), anchor="br")
    draw.rectangle([0,0,W,6], fill=AQUA)
    brand(draw)
    draw.text((44, 88), "“", font=f("Barlow-Bold.ttf", 110), fill=(*WHITE, 50))
    draw.text((54, 174), "They work", font=f("Barlow-Bold.ttf", 88), fill=WHITE)
    draw.text((54, 258), "harder than", font=f("Barlow-Bold.ttf", 88), fill=WHITE)
    draw.text((54, 342), "most adults", font=f("Barlow-Bold.ttf", 88), fill=WHITE)
    draw.text((54, 426), "I know.", font=f("Barlow-Bold.ttf", 88), fill=WHITE)
    draw.rectangle([54, 524, 290, 532], fill=AQUA)
    lines = ["Early mornings. Late practices.",
             "Competitions every weekend.",
             "They deserve a platform that",
             "keeps up with them."]
    for i, line in enumerate(lines):
        draw.text((54, 546+i*36), line, font=f("Barlow-Regular.ttf", 27), fill=GRAY)
    chips = ["Scheduling","Recruiting","AI Stats","Payments"]
    cx, cy = 54, 698
    fc = f("Barlow-SemiBold.ttf", 24)
    for chip in chips:
        cw = int(draw.textlength(chip, font=fc)) + 28
        rr(draw, [cx, cy, cx+cw, cy+40], r=20, outline=AQUA)
        draw.text((cx+14, cy+8), chip, font=fc, fill=AQUA)
        cx += cw + 10
    draw.text((54, 756), "From first practice to",
              font=f("Barlow-Regular.ttf", 24), fill=GRAY)
    draw.text((54, 784), "college signing.",
              font=f("Barlow-Bold.ttf", 38), fill=AQUA)
    cta(draw, "Free for parents  —  link in bio", 856, w=560)
    draw.text((54, 1046), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)
    img.save(f"{OUT}/post2_emotional.jpg", "JPEG", quality=95)
    print("post2 ✓")


# ─── POST 3 — Finally. One app. ───────────────────────────────────────────────
def post3():
    img = Image.new("RGB", (W,H), DARK)
    draw = ImageDraw.Draw(img)
    paste_cut(img, "/tmp/phone_nobg.png", w=600, pos=(1072, 540), anchor="tr")
    draw.rectangle([0,0,W,6], fill=AQUA)
    brand(draw)
    draw.text((54, 104), "Finally.", font=f("Barlow-Bold.ttf", 80), fill=AQUA)
    draw.text((54, 188), "One app for everything.", font=f("Barlow-Bold.ttf", 50), fill=WHITE)
    draw.rectangle([54, 248, 220, 256], fill=AQUA)
    items = ["Practice & game schedules","Team payments & fees",
             "Coach updates & announcements","Athlete stats & highlights",
             "College recruiting profile"]
    y = 268
    for item in items:
        rr(draw, [50, y-2, 570, y+32], r=8, fill=DARK2)
        draw.ellipse([56, y+2, 80, y+26], fill=AQUA)
        draw.text((62, y+3), "+", font=f("Barlow-Bold.ttf", 20), fill=DARK)
        draw.text((92, y+2), item, font=f("Barlow-Regular.ttf", 26), fill=WHITE)
        y += 48
    draw.text((54, y+10), "Built by a sports mom.", font=f("Barlow-SemiBold.ttf", 28), fill=WHITE)
    draw.text((54, y+46), "Free to join.", font=f("Barlow-Bold.ttf", 28), fill=AQUA)
    cta(draw, "Sign up free  —  teamthrive.com", y+92, w=560)
    draw.text((54, 1046), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)
    img.save(f"{OUT}/post3_checklist.jpg", "JPEG", quality=95)
    print("post3 ✓")


# ─── POST 4 — 6 apps vs 1 ────────────────────────────────────────────────────
def post4():
    img = Image.new("RGB", (W,H), DARK)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 480], fill=(12, 6, 16))
    brand(draw)
    draw.text((54, 120), "6 apps.", font=f("Barlow-Bold.ttf", 100), fill=SALMON)
    draw.text((54, 228), "to manage your kid's sports life.",
              font=f("Barlow-Regular.ttf", 30), fill=GRAY)
    apps_L = ["TeamSnap","GroupMe","Venmo"]
    apps_R = ["NCSA","Email / PDFs","Excel Sheets"]
    fa = f("Barlow-SemiBold.ttf", 24)
    for i, app in enumerate(apps_L):
        rr(draw, [54, 278+i*56, 510, 278+i*56+46], r=8, fill=(30, 14, 30))
        draw.rectangle([54, 278+i*56, 60, 278+i*56+46], fill=SALMON)
        draw.text((72, 278+i*56+11), app, font=fa, fill=WHITE)
    for i, app in enumerate(apps_R):
        rr(draw, [570, 278+i*56, 1026, 278+i*56+46], r=8, fill=(30, 14, 30))
        draw.rectangle([570, 278+i*56, 576, 278+i*56+46], fill=SALMON)
        draw.text((588, 278+i*56+11), app, font=fa, fill=WHITE)
    draw.rectangle([0, 480, W, 536], fill=DARK2)
    draw.line([(54,508),(460,508)], fill=AQUA, width=2)
    draw.line([(620,508),(1026,508)], fill=AQUA, width=2)
    draw.text((490, 490), "OR", font=f("Barlow-Bold.ttf", 28), fill=AQUA)
    draw.text((54, 556), "1 app.", font=f("Barlow-Bold.ttf", 100), fill=AQUA)
    feats = [["Scheduling","Payments"],["Stats & Tracking","Recruiting"]]
    ff = f("Barlow-SemiBold.ttf", 26)
    fy = 680
    for row in feats:
        for i, feat in enumerate(row):
            fx = 54 + i*492
            rr(draw, [fx, fy, fx+472, fy+54], r=10, fill=DARK2)
            draw.rectangle([fx, fy, fx+6, fy+54], fill=AQUA)
            draw.text((fx+18, fy+14), feat, font=ff, fill=WHITE)
        fy += 68
    draw.text((54, 824), "Team Thrive.", font=f("Barlow-Bold.ttf", 36), fill=WHITE)
    draw.text((54, 862), "Free for parents.", font=f("Barlow-Bold.ttf", 28), fill=AQUA)
    cta(draw, "Link in bio  —  teamthrive.com", 918)
    draw.text((54, 1046), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)
    img.save(f"{OUT}/post4_contrast.jpg", "JPEG", quality=95)
    print("post4 ✓")


# ─── POST 5 — You drove an hour ───────────────────────────────────────────────
def post5():
    img = Image.new("RGB", (W,H), DARK)
    draw = ImageDraw.Draw(img)
    paste_cut(img, "/tmp/soccer_nobg.png", h=780, pos=(W,H), anchor="br")
    draw.rectangle([0,0,W,6], fill=AQUA)
    brand(draw)
    draw.text((54, 110), "You drove an hour", font=f("Barlow-Bold.ttf", 60), fill=WHITE)
    draw.text((54, 172), "to watch them play.", font=f("Barlow-Bold.ttf", 60), fill=WHITE)
    draw.rectangle([54, 242, 300, 250], fill=AQUA)
    draw.text((54, 268), "Then spent the whole warmup", font=f("Barlow-Regular.ttf", 32), fill=GRAY)
    draw.text((54, 306), "digging through emails", font=f("Barlow-Regular.ttf", 32), fill=GRAY)
    draw.text((54, 344), "just to find the start time.", font=f("Barlow-Regular.ttf", 32), fill=GRAY)
    chaos = ["Schedule buried in a text thread",
             "Payment link in a PDF somewhere",
             "Roster update — which version?"]
    y = 406
    for item in chaos:
        rr(draw, [54, y, 590, y+50], r=8, fill=DARK2)
        draw.rectangle([54, y, 60, y+50], fill=SALMON)
        draw.text((72, y+13), item, font=f("Barlow-Regular.ttf", 25), fill=GRAY)
        y += 64
    draw.text((54, y+16), "You deserve better.", font=f("Barlow-Bold.ttf", 46), fill=WHITE)
    draw.text((54, y+70), "Team Thrive organizes everything",
              font=f("Barlow-SemiBold.ttf", 30), fill=AQUA)
    draw.text((54, y+108), "before you pull into the parking lot.",
              font=f("Barlow-SemiBold.ttf", 30), fill=AQUA)
    cta_y = y + 158
    rr(draw, [54, cta_y, 654, cta_y+88], r=16, fill=AQUA)
    ct = "Free to join  —  teamthrive.com"
    tw = draw.textlength(ct, font=f("Barlow-Bold.ttf", 30))
    draw.text((54+(600-tw)/2, cta_y+28), ct, font=f("Barlow-Bold.ttf", 30), fill=DARK)
    draw.text((54, 1046), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)
    img.save(f"{OUT}/post5_bigpicture.jpg", "JPEG", quality=95)
    print("post5 ✓")


# ─── POST 6 — Tag a sports parent ────────────────────────────────────────────
def post6():
    img = Image.new("RGB", (W,H), DARK)
    draw = ImageDraw.Draw(img)
    for i in range(12):
        off = 40 + i*22
        draw.line([(W-off, 0), (W, off)], fill=(*AQUA, 40), width=2)
    brand(draw)
    draw.text((54, 108), "Tag a sports", font=f("Barlow-Bold.ttf", 100), fill=WHITE)
    draw.text((54, 204), "parent who needs", font=f("Barlow-Bold.ttf", 100), fill=WHITE)
    draw.text((54, 300), "this.", font=f("Barlow-Bold.ttf", 100), fill=AQUA)
    draw.rectangle([54, 412, 160, 420], fill=AQUA)
    rows = ["One app for every sport.",
            "Schedules, payments, recruiting & updates.",
            "Free for parents."]
    y = 436
    for row in rows:
        rr(draw, [54, y, 1026, y+60], r=10, fill=DARK2)
        draw.rectangle([54, y, 62, y+60], fill=AQUA)
        draw.text((80, y+16), row, font=f("Barlow-SemiBold.ttf", 27), fill=WHITE)
        y += 74
    draw.text((54, y+14), "Built by a sports mom.",
              font=f("Barlow-Regular.ttf", 26), fill=GRAY)
    cta(draw, "Sign up free  —  teamthrive.com", y+56)
    draw.text((54, 1046), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)
    img.save(f"{OUT}/post6_tag.jpg", "JPEG", quality=95)
    print("post6 ✓")


# ─── POST 7 — Your phone right now ───────────────────────────────────────────
def post7():
    img = Image.new("RGB", (W,H), DARK)
    draw = ImageDraw.Draw(img)
    brand(draw)
    draw.text((54, 120), "Your phone", font=f("Barlow-Bold.ttf", 100), fill=WHITE)
    draw.text((54, 218), "right now:", font=f("Barlow-Bold.ttf", 100), fill=SALMON)
    draw.rectangle([54, 330, 160, 338], fill=SALMON)
    notifications = [
        ("GroupMe", '(14)  "Who has the hotel block code?"'),
        ("Email",   "(7)   Meet schedule changed AGAIN"),
        ("TeamSnap","(3)   Payment due — 2nd notice"),
        ("Random PDF", "Roster_FINAL_v3_USE THIS ONE"),
        ("Excel Sheet","Practice times (maybe outdated)"),
    ]
    y = 354
    for app, msg in notifications:
        rr(draw, [54, y, 1026, y+80], r=10, fill=DARK2)
        draw.rectangle([54, y, 60, y+80], fill=AQUA)
        draw.text((72, y+12), app, font=f("Barlow-SemiBold.ttf", 26), fill=AQUA)
        draw.text((72, y+44), msg, font=f("Barlow-Regular.ttf", 24), fill=GRAY)
        y += 92
    draw.text((54, y+10), "There is a better way.",
              font=f("Barlow-Bold.ttf", 42), fill=WHITE)
    draw.text((54, y+60), "Everything above. One app.",
              font=f("Barlow-SemiBold.ttf", 30), fill=AQUA)
    cta(draw, "Free to join  —  link in bio", y+108)
    draw.text((54, 1046), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)
    img.save(f"{OUT}/post7_phone.jpg", "JPEG", quality=95)
    print("post7 ✓")


# ─── POST 9 — WE'RE LIVE ─────────────────────────────────────────────────────
def post9():
    img = Image.new("RGB", (W,H), DARK)
    draw = ImageDraw.Draw(img)
    paste_cut(img, "/tmp/phone_nobg.png", w=520, pos=(1084, 880), anchor="br")
    draw.rectangle([0,0,W,8], fill=AQUA)
    brand(draw)
    ft_b = f("Barlow-Bold.ttf", 26)
    bw = int(draw.textlength("NOW LIVE", font=ft_b)) + 40
    rr(draw, [54, 104, 54+bw, 152], r=24, fill=AQUA)
    draw.text((74, 115), "NOW LIVE", font=ft_b, fill=DARK)
    draw.text((54, 172), "WE'RE", font=f("Barlow-Bold.ttf", 148), fill=WHITE)
    draw.text((54, 316), "LIVE.", font=f("Barlow-Bold.ttf", 148), fill=AQUA)
    draw.rectangle([54, 472, 310, 480], fill=AQUA)
    draw.text((54, 492), "Team Thrive is officially here.",
              font=f("Barlow-SemiBold.ttf", 34), fill=WHITE)
    draw.text((54, 534), "All-in-one for youth sports families.",
              font=f("Barlow-Regular.ttf", 27), fill=GRAY)
    feats = ["Schedules & payments","Athlete stats — every season",
             "College recruiting profile","Free for parents. Always."]
    fy = 596
    for feat in feats:
        rr(draw, [54, fy, 490, fy+50], r=10, fill=DARK2)
        draw.rectangle([54, fy, 59, fy+50], fill=AQUA)
        draw.text((70, fy+12), feat, font=f("Barlow-Regular.ttf", 26), fill=WHITE)
        fy += 62
    cta(draw, "Download now  —  teamthrive.com", 898)
    draw.text((54, 1048), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)
    img.save(f"{OUT}/post9_live.jpg", "JPEG", quality=95)
    print("post9 ✓")


# ─── POST 10 — Before / After ─────────────────────────────────────────────────
def post10():
    img = Image.new("RGB", (W,H), DARK)
    draw = ImageDraw.Draw(img)
    SPLIT = 530; COL_H = 800
    draw.rectangle([0, 0, SPLIT, COL_H], fill=DARK_BG_SPLIT_L)
    draw.rectangle([SPLIT, 0, W, COL_H], fill=DARK_BG_SPLIT_R)
    brand(draw, x=46, y=36)
    draw.text((46,92), "BEFORE", font=f("Barlow-Bold.ttf", 64), fill=SALMON)
    draw.rectangle([46,164,200,170], fill=SALMON)
    before = ["Group chat overload","Missed schedule updates",
              "3 different payment apps","No record of progress","Recruiting? Figure it out."]
    y = 184
    for item in before:
        draw.text((46,y), "—  "+item, font=f("Barlow-Regular.ttf", 26), fill=(200,150,150))
        y += 52
    items_end = y
    draw.text((SPLIT+36,92), "AFTER", font=f("Barlow-Bold.ttf", 64), fill=AQUA)
    draw.rectangle([SPLIT+36,164,SPLIT+190,170], fill=AQUA)
    after = ["One app, all updates","Real-time notifications","One-tap payments",
             "Full season stats saved","Recruiting profile: built"]
    y2 = 184
    fa = f("Barlow-SemiBold.ttf", 26)
    for item in after:
        tw = draw.textlength(item, font=fa)
        draw.text((SPLIT+36,y2), item, font=fa, fill=AQUA)
        draw.text((SPLIT+36+tw+8,y2), "+", font=fa, fill=AQUA)
        y2 += 52
    paste_cut(img, "/tmp/phone_nobg.png", w=320, pos=(1068, COL_H-16), anchor="br")
    vs_font = f("Barlow-Bold.ttf", 56)
    vs_w = draw.textlength("VS", font=vs_font)
    vs_x = int(SPLIT - vs_w/2)
    vs_y = items_end + 24
    rr(draw, [vs_x-16, vs_y-8, vs_x+int(vs_w)+16, vs_y+64], r=10, fill=DARK2)
    draw.text((vs_x, vs_y), "VS", font=vs_font, fill=WHITE)
    draw.line([(SPLIT, 0), (SPLIT, vs_y-12)], fill=(60,80,110), width=2)
    draw.line([(SPLIT, vs_y+72), (SPLIT, COL_H)], fill=(60,80,110), width=2)
    draw.rectangle([0,COL_H,W,H], fill=DARK2)
    draw.rectangle([0,COL_H,W,COL_H+4], fill=AQUA)
    draw.text((46,COL_H+28), "The switch takes 2 minutes.",
              font=f("Barlow-Bold.ttf", 40), fill=WHITE)
    draw.text((46,COL_H+76), "The difference is the whole season.",
              font=f("Barlow-SemiBold.ttf", 30), fill=AQUA)
    draw.text((46,1044), "teamthrive.com  —  free to join",
              font=f("Barlow-Regular.ttf", 24), fill=GRAY)
    img.save(f"{OUT}/post10_beforeafter.jpg", "JPEG", quality=95)
    print("post10 ✓")


# ─── POST 11 — Athletic action (poster style) ─────────────────────────────────
def post11():
    """New post — poster-matched dark aesthetic with athlete action shots."""
    img = Image.new("RGB", (W,H), DARK)
    draw = ImageDraw.Draw(img)

    # Background — teal glow behind athlete
    for r_size in range(400, 50, -40):
        alpha = int(18 * (1 - r_size/400))
        draw.ellipse([W//2+80-r_size, H//2-r_size, W//2+80+r_size, H//2+r_size],
                     fill=(*AQUA, alpha))

    # Athlete + soccer ball — centered-right, large
    paste_cut(img, "/tmp/soccer_nobg.png", h=900, pos=(W+40, H+40), anchor="br")

    # Diagonal speed lines
    for i in range(5):
        y_line = 200 + i * 80
        x_off  = i * 30
        draw.line([(x_off, y_line), (550+x_off, y_line-120)],
                  fill=(*AQUA, 30+i*8), width=2)

    # Top — logo area
    draw.rectangle([0,0,W,8], fill=AQUA)
    brand(draw, x=54, y=48)

    # Bold headline — left side
    draw.text((54, 110), "POWER.", font=f("Barlow-Bold.ttf", 96), fill=WHITE)
    draw.text((54, 202), "DRIVE.", font=f("Barlow-Bold.ttf", 96), fill=WHITE)
    draw.text((54, 294), "THRIVE.", font=f("Barlow-Bold.ttf", 96), fill=AQUA)

    # Stars under headline
    stars(draw, 130, 406, n=3, size=10)

    # Teal accent line
    draw.rectangle([54, 428, 320, 434], fill=AQUA)

    # Sub-copy
    draw.text((54, 454), "Your athlete works hard every day.",
              font=f("Barlow-SemiBold.ttf", 30), fill=WHITE)
    draw.text((54, 492), "Their stats, schedule, and story",
              font=f("Barlow-Regular.ttf", 28), fill=GRAY)
    draw.text((54, 526), "deserve a platform to match.",
              font=f("Barlow-Regular.ttf", 28), fill=GRAY)

    # Feature pills
    feats = ["Track every season", "Build their recruiting profile",
             "Share highlights", "Free for families"]
    fy = 578
    for feat in feats:
        rr(draw, [54, fy, 530, fy+48], r=24, fill=DARK2)
        draw.ellipse([62, fy+14, 80, fy+32], fill=AQUA)
        draw.text((90, fy+12), feat, font=f("Barlow-Regular.ttf", 26), fill=WHITE)
        fy += 62

    # CTA
    cta(draw, "Download free  —  teamthrive.com", fy+14, w=680)

    # Bottom stars + tagline
    draw.text((54, H-56), "TRAIN  |  COMPETE  |  THRIVE",
              font=f("Barlow-Bold.ttf", 22), fill=(*AQUA, 160))

    img.save(f"{OUT}/post11_athletic.jpg", "JPEG", quality=95)
    print("post11 ✓")


# ─── COMPILE PDF ──────────────────────────────────────────────────────────────
def compile_pdf():
    files = ["post1_chaos.jpg","post2_emotional.jpg","post3_checklist.jpg",
             "post4_contrast.jpg","post5_bigpicture.jpg","post6_tag.jpg",
             "post7_phone.jpg","post9_live.jpg","post10_beforeafter.jpg",
             "post11_athletic.jpg"]
    imgs = [Image.open(f"{OUT}/{fn}").convert("RGB") for fn in files]
    imgs[0].save(f"{OUT}/team-thrive-instagram-posts.pdf",
                 "PDF", save_all=True, append_images=imgs[1:], resolution=150)
    print(f"PDF saved — {len(imgs)} posts")


if __name__ == "__main__":
    post1(); post2(); post3(); post4(); post5()
    post6(); post7(); post9(); post10(); post11()
    compile_pdf()
