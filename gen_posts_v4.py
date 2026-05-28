#!/usr/bin/env python3
"""
Rebuild posts with clean background-removed images (no blending hacks).
"""

from PIL import Image, ImageDraw, ImageFont
import os

FONTS_DIR = "/tmp/fonts"
OUT_DIR   = "/home/user/team-thrive/instagram"
SIZE      = (1080, 1080)

NAVY   = (17,  30,  60)
NAVY2  = (24,  40,  80)
TEAL   = (61, 220, 132)
WHITE  = (255, 255, 255)
GRAY   = (160, 175, 200)

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS_DIR, name), size)

def brand_header(draw):
    f_reg  = font("Barlow-Regular.ttf", 28)
    f_bold = font("Barlow-Bold.ttf", 28)
    draw.text((54, 52), "TEAM ", font=f_reg, fill=WHITE)
    w = draw.textlength("TEAM ", font=f_reg)
    draw.text((54 + w, 52), "THRIVE", font=f_bold, fill=TEAL)

def rounded_rect(draw, xy, radius, fill=None, outline=None, outline_width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill,
                           outline=outline, width=outline_width)

def cta_button(draw, text, y, x=54, w=972, fill=TEAL, fg=NAVY):
    rounded_rect(draw, [x, y, x+w, y+88], radius=16, fill=fill)
    f = font("Barlow-Bold.ttf", 34)
    tw = draw.textlength(text, font=f)
    draw.text((x + (w - tw) / 2, y + 26), text, font=f, fill=fg)

def paste_cutout(base, path, target_w=None, target_h=None, pos=(0, 0), anchor="tl"):
    """Paste a background-removed PNG onto base. Scale by target_w or target_h."""
    src = Image.open(path).convert("RGBA")
    sw, sh = src.size
    if target_w:
        scale = target_w / sw
        src = src.resize((int(sw*scale), int(sh*scale)), Image.LANCZOS)
    elif target_h:
        scale = target_h / sh
        src = src.resize((int(sw*scale), int(sh*scale)), Image.LANCZOS)
    fw, fh = src.size
    x, y = pos
    if anchor == "br":   # bottom-right
        x, y = x - fw, y - fh
    elif anchor == "bc": # bottom-center
        x, y = x - fw//2, y - fh
    elif anchor == "tr": # top-right
        x, y = x - fw, y
    base.paste(src, (x, y), src)
    return fw, fh


# ─────────────────────────────────────────────────────────────────────────────
# POST 2 — "They work harder" + basketball girl cutout
# ─────────────────────────────────────────────────────────────────────────────
def make_post2():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # Athlete — bottom-right anchored, fills right 44% of image
    # img_50 is 999x1499. Scale so height fills bottom 800px, bottom-right corner
    paste_cutout(img, "/tmp/athlete_nobg.png",
                 target_h=880, pos=(1080, 1080), anchor="br")

    # Subtle teal top accent stripe
    draw.rectangle([0, 0, 1080, 6], fill=TEAL)

    brand_header(draw)

    # Large open-quote decoration
    draw.text((44, 88), "“", font=font("Barlow-Bold.ttf", 110),
              fill=(255, 255, 255, 60))

    # Headline
    f_h = font("Barlow-Bold.ttf", 88)
    draw.text((54, 174), "They work", font=f_h, fill=WHITE)
    draw.text((54, 258), "harder than", font=f_h, fill=WHITE)
    draw.text((54, 342), "most adults", font=f_h, fill=WHITE)
    draw.text((54, 426), "I know.", font=f_h, fill=WHITE)

    # Teal underline
    draw.rectangle([54, 524, 290, 532], fill=TEAL)

    # Body
    f_b = font("Barlow-Regular.ttf", 27)
    for i, line in enumerate([
        "Early mornings. Late practices.",
        "Competitions every weekend.",
        "They deserve a platform that",
        "keeps up with them.",
    ]):
        draw.text((54, 546 + i*36), line, font=f_b, fill=GRAY)

    # Feature chips
    chips = ["Scheduling", "Recruiting", "AI Stats", "Payments"]
    f_chip = font("Barlow-SemiBold.ttf", 24)
    cx, cy = 54, 698
    for chip in chips:
        cw = int(draw.textlength(chip, font=f_chip)) + 28
        rounded_rect(draw, [cx, cy, cx+cw, cy+40], radius=20,
                     outline=TEAL, outline_width=2)
        draw.text((cx + 14, cy + 8), chip, font=f_chip, fill=TEAL)
        cx += cw + 10

    # "From first practice to college signing"
    draw.text((54, 756), "From first practice to",
              font=font("Barlow-Regular.ttf", 24), fill=GRAY)
    draw.text((54, 784), "college signing.",
              font=font("Barlow-Bold.ttf", 38), fill=TEAL)

    cta_button(draw, "Free for parents  —  link in bio", 856, w=560)

    draw.text((54, 1046), "teamthrive.com",
              font=font("Barlow-Regular.ttf", 22), fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post2_emotional.jpg"), "JPEG", quality=95)
    print("post2_emotional.jpg saved")


# ─────────────────────────────────────────────────────────────────────────────
# POST 3 — checklist + phone mockup floating right
# ─────────────────────────────────────────────────────────────────────────────
def make_post3():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # Phone mockup — right side, scaled to 600px wide, vertically centered
    pw, ph = paste_cutout(img, "/tmp/phone_nobg.png",
                          target_w=600, pos=(1072, 540), anchor="tr")

    draw.rectangle([0, 0, 1080, 6], fill=TEAL)
    brand_header(draw)

    # Headline
    draw.text((54, 104), "Finally.", font=font("Barlow-Bold.ttf", 80), fill=TEAL)
    draw.text((54, 188), "One app for everything.",
              font=font("Barlow-Bold.ttf", 50), fill=WHITE)
    draw.rectangle([54, 248, 220, 256], fill=TEAL)

    # Checklist
    items = [
        "Practice & game schedules",
        "Team payments & fees",
        "Coach updates & announcements",
        "Athlete stats & highlights",
        "College recruiting profile",
    ]
    f_item = font("Barlow-Regular.ttf", 26)
    y = 268
    for item in items:
        rounded_rect(draw, [50, y - 2, 570, y + 32], radius=8, fill=NAVY2)
        draw.ellipse([56, y + 2, 80, y + 26], fill=TEAL)
        draw.text((62, y + 3), "+", font=font("Barlow-Bold.ttf", 20), fill=NAVY)
        draw.text((92, y + 2), item, font=f_item, fill=WHITE)
        y += 48

    draw.text((54, y + 10), "Built by a sports mom.",
              font=font("Barlow-SemiBold.ttf", 28), fill=WHITE)
    draw.text((54, y + 46), "Free to join.",
              font=font("Barlow-Bold.ttf", 28), fill=TEAL)

    cta_button(draw, "Sign up free  —  teamthrive.com", y + 92, w=560)

    draw.text((54, 1046), "teamthrive.com",
              font=font("Barlow-Regular.ttf", 22), fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post3_checklist.jpg"), "JPEG", quality=95)
    print("post3_checklist.jpg saved")


# ─────────────────────────────────────────────────────────────────────────────
# POST 9 — WE'RE LIVE + phone mockup floating right side
# ─────────────────────────────────────────────────────────────────────────────
def make_post9():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # Phone mockup — right half, tall, bottom-anchored
    paste_cutout(img, "/tmp/phone_nobg.png",
                 target_w=580, pos=(1088, 1060), anchor="br")

    draw.rectangle([0, 0, 1080, 8], fill=TEAL)
    brand_header(draw)

    # NOW LIVE badge
    badge = "  NOW LIVE  "
    f_b = font("Barlow-Bold.ttf", 26)
    bw = int(draw.textlength(badge, font=f_b)) + 20
    rounded_rect(draw, [54, 104, 54 + bw, 152], radius=24, fill=TEAL)
    draw.text((64, 115), badge.strip(), font=f_b, fill=NAVY)

    # Big headline
    f_huge = font("Barlow-Bold.ttf", 148)
    draw.text((54, 164), "WE'RE", font=f_huge, fill=WHITE)
    draw.text((54, 308), "LIVE.", font=f_huge, fill=TEAL)

    draw.rectangle([54, 464, 330, 472], fill=TEAL)

    draw.text((54, 482), "Team Thrive is officially here.",
              font=font("Barlow-SemiBold.ttf", 34), fill=WHITE)
    draw.text((54, 524), "All-in-one for youth sports families.",
              font=font("Barlow-Regular.ttf", 27), fill=GRAY)

    # Feature bullets — left column, bottom area
    features = [
        "Schedules & payments",
        "Athlete stats — every season",
        "College recruiting profile",
        "Free for parents. Always.",
    ]
    f_feat = font("Barlow-Regular.ttf", 26)
    fy = 590
    for feat in features:
        rounded_rect(draw, [54, fy, 490, fy + 50], radius=10, fill=NAVY2)
        draw.rectangle([54, fy, 59, fy + 50], fill=TEAL)
        draw.text((70, fy + 12), feat, font=f_feat, fill=WHITE)
        fy += 62

    cta_button(draw, "Download now  —  teamthrive.com", 862)

    draw.text((54, 1046), "teamthrive.com",
              font=font("Barlow-Regular.ttf", 22), fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post9_live.jpg"), "JPEG", quality=95)
    print("post9_live.jpg saved")


# ─────────────────────────────────────────────────────────────────────────────
# COMPILE PDF
# ─────────────────────────────────────────────────────────────────────────────
def compile_pdf():
    files = [
        "post1_chaos.jpg",
        "post2_emotional.jpg",
        "post3_checklist.jpg",
        "post4_contrast.jpg",
        "post5_bigpicture.jpg",
        "post6_tag.jpg",
        "post7_phone.jpg",
        "post9_live.jpg",
        "post10_beforeafter.jpg",
    ]
    images = [Image.open(os.path.join(OUT_DIR, f)).convert("RGB") for f in files]
    pdf_path = os.path.join(OUT_DIR, "team-thrive-instagram-posts.pdf")
    images[0].save(pdf_path, "PDF", save_all=True,
                   append_images=images[1:], resolution=150)
    print(f"PDF saved: {pdf_path}  ({len(images)} posts)")


if __name__ == "__main__":
    make_post2()
    make_post3()
    make_post9()
    compile_pdf()
