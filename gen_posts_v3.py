#!/usr/bin/env python3
"""
Rebuild posts with images:
  post2_emotional  — "they" gender fix + basketball girl athlete photo
  post3_checklist  — phone mockup added right side
  post9_live       — phone mockup added left side
Then recompile 9-post PDF.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

FONTS_DIR = "/tmp/fonts"
IMGS_DIR  = "/tmp/deck_imgs"
OUT_DIR   = "/home/user/team-thrive/instagram"
SIZE      = (1080, 1080)

NAVY    = (17,  30,  60)
NAVY2   = (24,  40,  80)
NAVY3   = (12,  20,  45)
TEAL    = (61, 220, 132)
WHITE   = (255, 255, 255)
GRAY    = (160, 175, 200)
SALMON  = (255, 100,  90)

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS_DIR, name), size)

def brand_header(draw, color=WHITE):
    f_reg  = font("Barlow-Regular.ttf", 28)
    f_bold = font("Barlow-Bold.ttf", 28)
    draw.text((54, 52), "TEAM ", font=f_reg, fill=color)
    w = draw.textlength("TEAM ", font=f_reg)
    draw.text((54 + w, 52), "THRIVE", font=f_bold, fill=TEAL)

def rounded_rect(draw, xy, radius, fill, outline=None, outline_width=0):
    draw.rounded_rectangle(xy, radius=radius, fill=fill,
                           outline=outline, width=outline_width)

def cta_button(draw, text, y, x=54, w=972, h=88, fill=TEAL, fg=NAVY):
    rounded_rect(draw, [x, y, x+w, y+h], radius=16, fill=fill)
    f = font("Barlow-Bold.ttf", 34)
    tw = draw.textlength(text, font=f)
    draw.text((x + (w-tw)/2, y + (h-34)/2 - 2), text, font=f, fill=fg)

def paste_img(base, src_path, box, darken=0.0, keep_aspect=True):
    """Paste src image into base at box=(x0,y0,x1,y1), optionally darken."""
    src = Image.open(src_path).convert("RGBA")
    bw, bh = box[2]-box[0], box[3]-box[1]
    if keep_aspect:
        src.thumbnail((bw*2, bh*2), Image.LANCZOS)
        # center-crop to box
        sw, sh = src.size
        scale = max(bw/sw, bh/sh)
        nw, nh = int(sw*scale), int(sh*scale)
        src = src.resize((nw, nh), Image.LANCZOS)
        cx = (nw-bw)//2
        cy = (nh-bh)//2
        src = src.crop((cx, cy, cx+bw, cy+bh))
    else:
        src = src.resize((bw, bh), Image.LANCZOS)
    if darken > 0:
        src = ImageEnhance.Brightness(src).enhance(1.0 - darken)
    # composite onto base
    base_crop = base.crop(box)
    # if src has alpha, use it; else just paste
    if src.mode == 'RGBA':
        base.paste(src, (box[0], box[1]), src)
    else:
        base.paste(src.convert("RGB"), (box[0], box[1]))


# ─────────────────────────────────────────────────────────────────────────────
# POST 2 — "They work harder" + athlete image
# ─────────────────────────────────────────────────────────────────────────────
def make_post2():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # Right half: basketball girl photo
    # img_50 is 999x1499, portrait — fill right 480px column, full height
    src = Image.open(os.path.join(IMGS_DIR, "img_50.png")).convert("RGB")
    # Fit to right 480px wide, 1080 tall
    rw, rh = 480, 1080
    sw, sh = src.size
    scale = max(rw/sw, rh/sh)
    nw, nh = int(sw*scale), int(sh*scale)
    src = src.resize((nw, nh), Image.LANCZOS)
    cx = (nw-rw)//2
    cy = (nh-rh)//2
    src = src.crop((cx, cy, cx+rw, cy+rh))
    img.paste(src, (600, 0))

    # Gradient overlay on right side to blend text area
    grad = Image.new("RGBA", (280, 1080), (0,0,0,0))
    gd = ImageDraw.Draw(grad)
    for x in range(280):
        alpha = int(255 * (1 - x/280))
        gd.line([(x,0),(x,1080)], fill=(*NAVY, alpha))
    img.paste(grad, (600, 0), grad)

    # Teal top accent
    draw.rectangle([0, 0, 1080, 6], fill=TEAL)

    brand_header(draw)

    # Large quote mark
    f_q = font("Barlow-Bold.ttf", 120)
    draw.text((46, 88), "“", font=f_q, fill=(255,255,255,80))

    # Headline — "They work harder"
    f_h1 = font("Barlow-Bold.ttf", 86)
    draw.text((54, 170), "They work", font=f_h1, fill=WHITE)
    draw.text((54, 252), "harder than", font=f_h1, fill=WHITE)
    f_h2 = font("Barlow-Bold.ttf", 86)
    draw.text((54, 334), "most adults", font=f_h2, fill=WHITE)
    draw.text((54, 416), "I know.", font=f_h2, fill=WHITE)

    # teal underline
    draw.rectangle([54, 510, 280, 518], fill=TEAL)

    # Body
    f_b = font("Barlow-Regular.ttf", 28)
    lines = [
        "Early mornings. Late practices.",
        "Competitions every weekend.",
        "They deserve a platform that",
        "keeps up with them.",
    ]
    y = 530
    for line in lines:
        draw.text((54, y), line, font=f_b, fill=GRAY)
        y += 36

    # Feature chips
    chips = ["Scheduling", "Recruiting", "AI Stats", "Payments"]
    f_chip = font("Barlow-SemiBold.ttf", 24)
    cx2 = 54
    cy2 = 688
    for chip in chips:
        cw = int(draw.textlength(chip, font=f_chip)) + 28
        rounded_rect(draw, [cx2, cy2, cx2+cw, cy2+40], radius=20,
                     fill=(0,0,0,0), outline=TEAL, outline_width=2)
        draw.text((cx2+14, cy2+8), chip, font=f_chip, fill=TEAL)
        cx2 += cw + 12

    # "From first practice to college signing"
    f_sm = font("Barlow-Regular.ttf", 24)
    draw.text((54, 748), "From first practice to", font=f_sm, fill=GRAY)
    f_lg = font("Barlow-Bold.ttf", 38)
    draw.text((54, 776), "college signing.", font=f_lg, fill=TEAL)

    cta_button(draw, "Free for parents  —  link in bio", 848, w=560)

    f_foot = font("Barlow-Regular.ttf", 22)
    draw.text((54, 1042), "teamthrive.com", font=f_foot, fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post2_emotional.jpg"), "JPEG", quality=95)
    print("post2_emotional.jpg saved")


# ─────────────────────────────────────────────────────────────────────────────
# POST 3 — checklist + phone mockup right side
# ─────────────────────────────────────────────────────────────────────────────
def make_post3():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # Right side: phone mockup (img_00, 1490x1490) — right 420px
    src = Image.open(os.path.join(IMGS_DIR, "img_00.png")).convert("RGB")
    rw, rh = 480, 820
    sw, sh = src.size
    scale = max(rw/sw, rh/sh)
    nw, nh = int(sw*scale), int(sh*scale)
    src = src.resize((nw, nh), Image.LANCZOS)
    cx = (nw-rw)//2
    cy = max(0, (nh-rh)//2)
    src = src.crop((cx, cy, cx+rw, cy+rh))
    img.paste(src, (600, 140))

    # Left-side gradient to blend
    grad = Image.new("RGBA", (240, 1080), (0,0,0,0))
    gd = ImageDraw.Draw(grad)
    for x in range(240):
        alpha = int(255 * (1 - x/240))
        gd.line([(x,0),(x,1080)], fill=(*NAVY, alpha))
    img.paste(grad, (600, 0), grad)

    # Bottom gradient
    grad_b = Image.new("RGBA", (480, 160), (0,0,0,0))
    gdb = ImageDraw.Draw(grad_b)
    for y in range(160):
        alpha = int(255 * y/160)
        gdb.line([(0,y),(480,y)], fill=(*NAVY, alpha))
    img.paste(grad_b, (600, 920), grad_b)

    draw.rectangle([0, 0, 1080, 6], fill=TEAL)
    brand_header(draw)

    # Headline
    f_h = font("Barlow-Bold.ttf", 80)
    draw.text((54, 104), "Finally.", font=f_h, fill=TEAL)
    f_h2 = font("Barlow-Bold.ttf", 54)
    draw.text((54, 188), "One app for everything.", font=f_h2, fill=WHITE)
    draw.rectangle([54, 252, 220, 260], fill=TEAL)

    # Checklist items
    items = [
        "Practice & game schedules",
        "Team payments & fees",
        "Coach updates & announcements",
        "Athlete stats & highlights",
        "College recruiting profile",
    ]
    f_item = font("Barlow-Regular.ttf", 26)
    f_item_b = font("Barlow-SemiBold.ttf", 26)
    y = 276
    for item in items:
        # teal circle + plus
        draw.ellipse([54, y+2, 80, y+28], fill=TEAL)
        draw.text((61, y+4), "+", font=font("Barlow-Bold.ttf", 20), fill=NAVY)
        draw.text((92, y+2), item, font=f_item, fill=WHITE)
        # row bg
        rounded_rect(draw, [50, y-2, 570, y+34], radius=8, fill=NAVY2)
        draw.ellipse([54, y+2, 80, y+28], fill=TEAL)
        draw.text((62, y+3), "+", font=font("Barlow-Bold.ttf", 20), fill=NAVY)
        draw.text((92, y+2), item, font=f_item, fill=WHITE)
        y += 50

    # Built by / free
    f_sm = font("Barlow-SemiBold.ttf", 28)
    draw.text((54, y+10), "Built by a sports mom.", font=f_sm, fill=WHITE)
    f_teal = font("Barlow-Bold.ttf", 28)
    draw.text((54, y+46), "Free to join.", font=f_teal, fill=TEAL)

    cta_button(draw, "Sign up free  —  teamthrive.com", y+96, w=560)

    f_foot = font("Barlow-Regular.ttf", 22)
    draw.text((54, 1042), "teamthrive.com", font=f_foot, fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post3_checklist.jpg"), "JPEG", quality=95)
    print("post3_checklist.jpg saved")


# ─────────────────────────────────────────────────────────────────────────────
# POST 9 — WE'RE LIVE + phone mockup
# ─────────────────────────────────────────────────────────────────────────────
def make_post9():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # Phone mockup — large, left-of-center
    src = Image.open(os.path.join(IMGS_DIR, "img_00.png")).convert("RGB")
    mw, mh = 460, 460
    src.thumbnail((mw, mh), Image.LANCZOS)
    sw, sh = src.size
    img.paste(src, (54, 580))

    # Right gradient to blend phone into bg
    grad = Image.new("RGBA", (200, 460), (0,0,0,0))
    gd = ImageDraw.Draw(grad)
    for x in range(200):
        alpha = int(255 * x/200)
        gd.line([(x,0),(x,460)], fill=(*NAVY, alpha))
    img.paste(grad, (54+sw-200, 580), grad)

    # Bottom gradient over phone
    grad_b = Image.new("RGBA", (sw, 120), (0,0,0,0))
    gdb = ImageDraw.Draw(grad_b)
    for y in range(120):
        alpha = int(255 * y/120)
        gdb.line([(0,y),(sw,y)], fill=(*NAVY, alpha))
    img.paste(grad_b, (54, 580+sh-120), grad_b)

    # teal top accent
    draw.rectangle([0, 0, 1080, 8], fill=TEAL)

    brand_header(draw)

    # "NOW LIVE" badge
    badge = "  NOW LIVE  "
    f_b = font("Barlow-Bold.ttf", 26)
    bw = int(draw.textlength(badge, font=f_b)) + 20
    rounded_rect(draw, [54, 104, 54+bw, 152], radius=24, fill=TEAL)
    draw.text((64, 115), badge.strip(), font=f_b, fill=NAVY)

    # Headline
    f_huge = font("Barlow-Bold.ttf", 136)
    draw.text((54, 162), "WE'RE", font=f_huge, fill=WHITE)
    draw.text((54, 292), "LIVE.", font=f_huge, fill=TEAL)

    draw.rectangle([54, 436, 300, 444], fill=TEAL)

    f_sub = font("Barlow-SemiBold.ttf", 34)
    draw.text((54, 456), "Team Thrive is officially here.", font=f_sub, fill=WHITE)
    f_body = font("Barlow-Regular.ttf", 27)
    draw.text((54, 498), "All-in-one for youth sports families.", font=f_body, fill=GRAY)

    # Right column features (sits to the right of phone mockup)
    features = [
        "Schedules & payments",
        "Athlete stats — every season",
        "College recruiting profile",
        "Free for parents",
    ]
    f_feat = font("Barlow-Regular.ttf", 26)
    fy = 600
    fx = 560
    fw = 466
    for feat in features:
        rounded_rect(draw, [fx, fy, fx+fw, fy+50], radius=10, fill=NAVY2)
        draw.rectangle([fx, fy, fx+5, fy+50], fill=TEAL)
        draw.text((fx+16, fy+12), feat, font=f_feat, fill=WHITE)
        fy += 62

    cta_button(draw, "Download now  —  teamthrive.com", 918)

    f_foot = font("Barlow-Regular.ttf", 22)
    draw.text((54, 1048), "teamthrive.com", font=f_foot, fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post9_live.jpg"), "JPEG", quality=95)
    print("post9_live.jpg saved")


# ─────────────────────────────────────────────────────────────────────────────
# COMPILE PDF  (9 posts, no post8)
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
    images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:], resolution=150)
    print(f"PDF saved: {pdf_path}  ({len(images)} posts)")


if __name__ == "__main__":
    make_post2()
    make_post3()
    make_post9()
    compile_pdf()
