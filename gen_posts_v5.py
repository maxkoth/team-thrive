#!/usr/bin/env python3
"""Fix posts 1, 4, 5, 9, 10 then recompile PDF."""

from PIL import Image, ImageDraw, ImageFont
import os

FONTS_DIR = "/tmp/fonts"
OUT_DIR   = "/home/user/team-thrive/instagram"
SIZE      = (1080, 1080)

NAVY      = (17,  30,  60)
NAVY2     = (24,  40,  80)
NAVY_DARK = (10,  18,  42)
TEAL      = (61, 220, 132)
WHITE     = (255, 255, 255)
GRAY      = (160, 175, 200)
SALMON    = (255, 100,  90)

def f(name, size):
    return ImageFont.truetype(os.path.join(FONTS_DIR, name), size)

def brand(draw, x=54, y=52):
    draw.text((x, y), "TEAM ", font=f("Barlow-Regular.ttf", 28), fill=WHITE)
    w = draw.textlength("TEAM ", font=f("Barlow-Regular.ttf", 28))
    draw.text((x + w, y), "THRIVE", font=f("Barlow-Bold.ttf", 28), fill=TEAL)

def rr(draw, xy, r, fill=None, outline=None, ow=2):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=ow)

def cta(draw, text, y, x=54, w=972, h=88, fill=TEAL, fg=NAVY):
    rr(draw, [x, y, x+w, y+h], r=16, fill=fill)
    ft = f("Barlow-Bold.ttf", 34)
    tw = draw.textlength(text, font=ft)
    draw.text((x + (w-tw)/2, y + (h-34)/2 - 1), text, font=ft, fill=fg)

def paste_cut(base, path, w=None, h=None, pos=(0,0), anchor="tl"):
    src = Image.open(path).convert("RGBA")
    sw, sh = src.size
    if w:
        src = src.resize((w, int(sh*(w/sw))), Image.LANCZOS)
    elif h:
        src = src.resize((int(sw*(h/sh))), Image.LANCZOS) if False else \
              src.resize((int(sw*(h/sh)), h), Image.LANCZOS)
    fw, fh = src.size
    x, y = pos
    if anchor == "br": x, y = x-fw, y-fh
    elif anchor == "tr": x, y = x-fw, y
    elif anchor == "bc": x, y = x-fw//2, y-fh
    base.paste(src, (x, y), src)
    return fw, fh


# ─── POST 1 — fill dead space with 5th row + better spacing ──────────────────
def make_post1():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # Corner decoration
    for i in range(12):
        off = 40 + i * 22
        draw.line([(1080-off, 0), (1080, off)], fill=(*TEAL, 55), width=2)

    brand(draw)

    draw.text((54, 120), "Sound familiar?", font=f("Barlow-Bold.ttf", 86), fill=WHITE)
    draw.rectangle([54, 216, 200, 224], fill=TEAL)

    rows = [
        "4 unread texts in the team group chat",
        "2 emails from the club — still unopened",
        "Still don't know what time practice starts",
        "Coach updated the schedule... somewhere",
        "Payment reminder sitting in 3 different apps",
    ]
    y = 240
    for row in rows:
        rr(draw, [54, y, 1026, y+62], r=10, fill=NAVY2)
        draw.rectangle([54, y, 62, y+62], fill=TEAL)
        draw.text((80, y+17), row, font=f("Barlow-Regular.ttf", 27), fill=WHITE)
        y += 72

    draw.rectangle([54, y+8, 1026, y+12], fill=TEAL)

    draw.text((54, y+28), "Team Thrive puts it all in one place.",
              font=f("Barlow-Bold.ttf", 34), fill=WHITE)

    chips = ["Schedules", "Payments", "Updates", "Recruiting"]
    cx, cy = 54, y + 80
    fc = f("Barlow-SemiBold.ttf", 26)
    for chip in chips:
        cw = int(draw.textlength(chip, font=fc)) + 30
        rr(draw, [cx, cy, cx+cw, cy+44], r=22, outline=TEAL)
        draw.text((cx+15, cy+9), chip, font=fc, fill=TEAL)
        cx += cw + 14

    cta(draw, "Free to join  —  link in bio", cy + 62)
    draw.text((54, 1046), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post1_chaos.jpg"), "JPEG", quality=95)
    print("post1 saved")


# ─── POST 4 — fix colors, name the 6 apps, make bottom readable ──────────────
def make_post4():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # Top half — darker navy (not brown), distinct but on-brand
    draw.rectangle([0, 0, 1080, 480], fill=NAVY_DARK)

    brand(draw)

    draw.text((54, 120), "6 apps.", font=f("Barlow-Bold.ttf", 100), fill=SALMON)
    draw.text((54, 228), "to manage your kid's sports life.",
              font=f("Barlow-Regular.ttf", 30), fill=GRAY)

    # The 6 actual apps — two columns
    apps_L = ["TeamSnap", "GroupMe", "Venmo"]
    apps_R = ["NCSA", "Email / PDFs", "Excel Sheets"]
    fa = f("Barlow-SemiBold.ttf", 24)
    for i, app in enumerate(apps_L):
        rr(draw, [54, 278+i*56, 510, 278+i*56+46], r=8, fill=(30, 20, 55))
        draw.rectangle([54, 278+i*56, 60, 278+i*56+46], fill=SALMON)
        draw.text((72, 278+i*56+11), app, font=fa, fill=WHITE)
    for i, app in enumerate(apps_R):
        rr(draw, [570, 278+i*56, 1026, 278+i*56+46], r=8, fill=(30, 20, 55))
        draw.rectangle([570, 278+i*56, 576, 278+i*56+46], fill=SALMON)
        draw.text((588, 278+i*56+11), app, font=fa, fill=WHITE)

    # OR divider
    draw.rectangle([0, 480, 1080, 536], fill=NAVY2)
    draw.line([(54, 508), (460, 508)], fill=TEAL, width=2)
    draw.line([(620, 508), (1026, 508)], fill=TEAL, width=2)
    draw.text((490, 490), "OR", font=f("Barlow-Bold.ttf", 28), fill=TEAL)

    # Bottom half — Team Thrive solution
    draw.text((54, 556), "1 app.", font=f("Barlow-Bold.ttf", 100), fill=TEAL)

    feats = [["Scheduling", "Payments"], ["Stats & Tracking", "Recruiting"]]
    ff = f("Barlow-SemiBold.ttf", 26)
    fy = 680
    for row in feats:
        for i, feat in enumerate(row):
            fx = 54 + i * 492
            rr(draw, [fx, fy, fx+472, fy+54], r=10, fill=NAVY2)
            draw.rectangle([fx, fy, fx+6, fy+54], fill=TEAL)
            draw.text((fx+18, fy+14), feat, font=ff, fill=WHITE)
        fy += 68

    draw.text((54, 824), "Team Thrive.", font=f("Barlow-Bold.ttf", 36), fill=WHITE)
    draw.text((54, 862), "Free for parents.", font=f("Barlow-Bold.ttf", 28), fill=TEAL)

    cta(draw, "Link in bio  —  teamthrive.com", 918)
    draw.text((54, 1046), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post4_contrast.jpg"), "JPEG", quality=95)
    print("post4 saved")


# ─── POST 5 — emotional parent hook (scrapping pitch deck stats) ──────────────
def make_post5():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # Soccer boy cutout — right side, bottom anchored
    paste_cut(img, "/tmp/soccer_nobg.png", h=780, pos=(1080, 1080), anchor="br")

    draw.rectangle([0, 0, 1080, 6], fill=TEAL)
    brand(draw)

    # Headline
    draw.text((54, 118), "You drove an hour",
              font=f("Barlow-Bold.ttf", 60), fill=WHITE)
    draw.text((54, 180), "to watch them play.",
              font=f("Barlow-Bold.ttf", 60), fill=WHITE)
    draw.rectangle([54, 250, 300, 258], fill=TEAL)

    # Pain point — the moment
    draw.text((54, 278), "Then spent the whole warmup",
              font=f("Barlow-Regular.ttf", 32), fill=GRAY)
    draw.text((54, 316), "digging through emails",
              font=f("Barlow-Regular.ttf", 32), fill=GRAY)
    draw.text((54, 354), "just to find the start time.",
              font=f("Barlow-Regular.ttf", 32), fill=GRAY)

    # 3 mini chaos items
    chaos = ["Schedule buried in a text thread",
             "Payment link in a PDF somewhere",
             "Roster update — which version?"]
    fc = f("Barlow-Regular.ttf", 25)
    y = 416
    for item in chaos:
        rr(draw, [54, y, 590, y+48], r=8, fill=NAVY2)
        draw.rectangle([54, y, 60, y+48], fill=SALMON)
        draw.text((72, y+12), item, font=fc, fill=GRAY)
        y += 58

    # Resolution
    draw.text((54, 560), "You deserve better.", font=f("Barlow-Bold.ttf", 46), fill=WHITE)
    draw.text((54, 612), "Team Thrive organizes everything",
              font=f("Barlow-SemiBold.ttf", 30), fill=TEAL)
    draw.text((54, 648), "before you pull into the parking lot.",
              font=f("Barlow-SemiBold.ttf", 30), fill=TEAL)

    cta(draw, "Free to join  —  teamthrive.com", 716, w=600)
    draw.text((54, 1046), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post5_bigpicture.jpg"), "JPEG", quality=95)
    print("post5 saved")


# ─── POST 9 — fix phone overlapping CTA ──────────────────────────────────────
def make_post9():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # Phone — right side, vertically centered, doesn't touch bottom CTA zone
    paste_cut(img, "/tmp/phone_nobg.png", w=520, pos=(1084, 880), anchor="br")

    draw.rectangle([0, 0, 1080, 8], fill=TEAL)
    brand(draw)

    # NOW LIVE badge
    ft_b = f("Barlow-Bold.ttf", 26)
    bw = int(draw.textlength("NOW LIVE", font=ft_b)) + 40
    rr(draw, [54, 104, 54+bw, 152], r=24, fill=TEAL)
    draw.text((54+20, 115), "NOW LIVE", font=ft_b, fill=NAVY)

    # Big headline — left side only
    draw.text((54, 172), "WE'RE", font=f("Barlow-Bold.ttf", 148), fill=WHITE)
    draw.text((54, 316), "LIVE.", font=f("Barlow-Bold.ttf", 148), fill=TEAL)

    draw.rectangle([54, 472, 310, 480], fill=TEAL)
    draw.text((54, 492), "Team Thrive is officially here.",
              font=f("Barlow-SemiBold.ttf", 34), fill=WHITE)
    draw.text((54, 534), "All-in-one for youth sports families.",
              font=f("Barlow-Regular.ttf", 27), fill=GRAY)

    # 4 feature bullets — left column only, max 490px wide
    feats = ["Schedules & payments",
             "Athlete stats — every season",
             "College recruiting profile",
             "Free for parents. Always."]
    fy = 596
    for feat in feats:
        rr(draw, [54, fy, 490, fy+50], r=10, fill=NAVY2)
        draw.rectangle([54, fy, 59, fy+50], fill=TEAL)
        draw.text((70, fy+12), feat, font=f("Barlow-Regular.ttf", 26), fill=WHITE)
        fy += 62

    # Full-width CTA at bottom — below the phone bottom edge
    cta(draw, "Download now  —  teamthrive.com", 898)
    draw.text((54, 1048), "teamthrive.com", font=f("Barlow-Regular.ttf", 22), fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post9_live.jpg"), "JPEG", quality=95)
    print("post9 saved")


# ─── POST 10 — fill empty columns with phone mockup in After side ─────────────
def make_post10():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    SPLIT = 530
    COL_H = 800

    # Left — BEFORE (dark burgundy-navy)
    draw.rectangle([0, 0, SPLIT, COL_H], fill=(28, 12, 28))
    # Right — AFTER (dark teal-navy)
    draw.rectangle([SPLIT, 0, 1080, COL_H], fill=(8, 28, 28))

    brand(draw, x=46, y=36)

    # BEFORE header
    draw.text((46, 100), "BEFORE", font=f("Barlow-Bold.ttf", 64), fill=SALMON)
    draw.rectangle([46, 172, 200, 178], fill=SALMON)

    before = ["Group chat overload",
              "Missed schedule updates",
              "3 different payment apps",
              "No record of progress",
              "Recruiting? Figure it out."]
    fb = f("Barlow-Regular.ttf", 26)
    y = 194
    for item in before:
        draw.text((46, y), "—  " + item, font=fb, fill=(200, 160, 160))
        y += 50

    # AFTER header
    draw.text((SPLIT + 36, 100), "AFTER", font=f("Barlow-Bold.ttf", 64), fill=TEAL)
    draw.rectangle([SPLIT + 36, 172, SPLIT + 190, 178], fill=TEAL)

    after = ["One app, all updates",
             "Real-time notifications",
             "One-tap payments",
             "Full season stats saved",
             "Recruiting profile: built"]
    fa = f("Barlow-SemiBold.ttf", 26)
    y = 194
    for item in after:
        tw = draw.textlength(item, font=fa)
        draw.text((SPLIT + 36, y), item, font=fa, fill=TEAL)
        draw.text((SPLIT + 36 + tw + 8, y), "+", font=fa, fill=TEAL)
        y += 50

    # Phone mockup in the AFTER column empty space
    paste_cut(img, "/tmp/phone_nobg.png", w=340, pos=(1068, COL_H - 20), anchor="br")

    # VS divider — vertical center line
    draw.line([(SPLIT, 0), (SPLIT, COL_H)], fill=(80, 100, 140), width=3)
    draw.text((SPLIT - 22, COL_H//2 - 20), "VS",
              font=f("Barlow-Bold.ttf", 28), fill=(100, 120, 160))

    # Bottom strip
    draw.rectangle([0, COL_H, 1080, 1080], fill=NAVY2)
    draw.rectangle([0, COL_H, 1080, COL_H + 4], fill=TEAL)

    draw.text((46, COL_H + 28), "The switch takes 2 minutes.",
              font=f("Barlow-Bold.ttf", 40), fill=WHITE)
    draw.text((46, COL_H + 76), "The difference is the whole season.",
              font=f("Barlow-SemiBold.ttf", 30), fill=TEAL)

    draw.text((46, 1044), "teamthrive.com  —  free to join",
              font=f("Barlow-Regular.ttf", 24), fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post10_beforeafter.jpg"), "JPEG", quality=95)
    print("post10 saved")


# ─── COMPILE ──────────────────────────────────────────────────────────────────
def compile_pdf():
    files = ["post1_chaos.jpg", "post2_emotional.jpg", "post3_checklist.jpg",
             "post4_contrast.jpg", "post5_bigpicture.jpg", "post6_tag.jpg",
             "post7_phone.jpg", "post9_live.jpg", "post10_beforeafter.jpg"]
    imgs = [Image.open(os.path.join(OUT_DIR, fn)).convert("RGB") for fn in files]
    out = os.path.join(OUT_DIR, "team-thrive-instagram-posts.pdf")
    imgs[0].save(out, "PDF", save_all=True, append_images=imgs[1:], resolution=150)
    print(f"PDF saved — {len(imgs)} posts")


if __name__ == "__main__":
    make_post1()
    make_post4()
    make_post5()
    make_post9()
    make_post10()
    compile_pdf()
