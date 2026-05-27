#!/usr/bin/env python3
"""Rebuild post9 as a launch announcement, then recompile 9-post PDF (no post8)."""

from PIL import Image, ImageDraw, ImageFont
import os

FONTS_DIR = "/tmp/fonts"
OUT_DIR = "/home/user/team-thrive/instagram"
SIZE = (1080, 1080)

NAVY    = (17,  30,  60)
NAVY2   = (24,  40,  80)
TEAL    = (61, 220, 132)
WHITE   = (255, 255, 255)
GRAY    = (160, 175, 200)
DARK_TEAL = (10, 40, 30)
GREEN_BG = (20, 60, 40)

def font(name, size):
    path = os.path.join(FONTS_DIR, name)
    return ImageFont.truetype(path, size)

def brand_header(draw, img_w=1080):
    """Draw 'TEAM THRIVE' brand mark top-left."""
    f_reg  = font("Barlow-Regular.ttf", 28)
    f_bold = font("Barlow-Bold.ttf", 28)
    draw.text((54, 52), "TEAM ", font=f_reg, fill=WHITE)
    # measure "TEAM "
    w_team = draw.textlength("TEAM ", font=f_reg)
    draw.text((54 + w_team, 52), "THRIVE", font=f_bold, fill=TEAL)

def rounded_rect(draw, xy, radius, fill, outline=None, outline_width=0):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                            outline=outline, width=outline_width)

def draw_cta_button(draw, text, y, fill=TEAL, text_color=(17,30,60), width=972, x=54):
    rounded_rect(draw, [x, y, x + width, y + 88], radius=16, fill=fill)
    f = font("Barlow-Bold.ttf", 34)
    tw = draw.textlength(text, font=f)
    draw.text((x + (width - tw) / 2, y + 24), text, font=f, fill=text_color)


# ── POST 9 — LAUNCH ANNOUNCEMENT ─────────────────────────────────────────────
def make_post9():
    img = Image.new("RGB", SIZE, NAVY)
    draw = ImageDraw.Draw(img)

    # top accent strip
    draw.rectangle([0, 0, 1080, 8], fill=TEAL)

    brand_header(draw)

    # "NOW LIVE" badge
    badge_text = "  NOW LIVE  "
    f_badge = font("Barlow-Bold.ttf", 26)
    bw = draw.textlength(badge_text, font=f_badge) + 20
    rounded_rect(draw, [54, 104, 54 + bw, 104 + 48], radius=24, fill=TEAL)
    draw.text((54 + 10, 115), badge_text.strip(), font=f_badge, fill=NAVY)

    # Main headline
    f_huge = font("Barlow-Bold.ttf", 120)
    draw.text((54, 170), "WE'RE", font=f_huge, fill=WHITE)
    draw.text((54, 280), "LIVE.", font=f_huge, fill=TEAL)

    # teal underline
    draw.rectangle([54, 400, 240, 408], fill=TEAL)

    # subheading
    f_sub = font("Barlow-SemiBold.ttf", 38)
    draw.text((54, 428), "Team Thrive is officially available.", font=f_sub, fill=WHITE)

    f_body = font("Barlow-Regular.ttf", 30)
    draw.text((54, 482), "The all-in-one platform for youth sports families.", font=f_body, fill=GRAY)

    # Feature rows
    features = [
        "Schedules, payments & team updates — one place",
        "Athlete stats tracked from day one",
        "College recruiting profile, ready when they are",
        "Free for parents. Always.",
    ]
    f_feat = font("Barlow-Regular.ttf", 28)
    f_feat_b = font("Barlow-SemiBold.ttf", 28)
    y = 558
    for feat in features:
        rounded_rect(draw, [54, y, 1026, y + 54], radius=10, fill=NAVY2)
        # teal left bar
        draw.rectangle([54, y, 60, y + 54], fill=TEAL)
        draw.text((78, y + 13), feat, font=f_feat, fill=WHITE)
        y += 66

    # CTA
    draw_cta_button(draw, "Download now  —  teamthrive.com", y + 18)

    # footer
    f_sm = font("Barlow-Regular.ttf", 22)
    draw.text((54, 1042), "teamthrive.com", font=f_sm, fill=GRAY)

    img.save(os.path.join(OUT_DIR, "post9_live.jpg"), "JPEG", quality=95)
    print("post9_live.jpg saved")


# ── COMPILE PDF ───────────────────────────────────────────────────────────────
def compile_pdf():
    files = [
        "post1_chaos.jpg",
        "post2_emotional.jpg",
        "post3_checklist.jpg",
        "post4_contrast.jpg",
        "post5_bigpicture.jpg",
        "post6_tag.jpg",
        "post7_phone.jpg",
        "post9_live.jpg",       # replaces post9_fomo (post8 removed)
        "post10_beforeafter.jpg",
    ]
    images = []
    for f in files:
        path = os.path.join(OUT_DIR, f)
        im = Image.open(path).convert("RGB")
        images.append(im)

    pdf_path = os.path.join(OUT_DIR, "team-thrive-instagram-posts.pdf")
    images[0].save(
        pdf_path, "PDF", save_all=True, append_images=images[1:],
        resolution=150
    )
    print(f"PDF saved: {pdf_path} ({len(images)} posts)")


if __name__ == "__main__":
    make_post9()
    compile_pdf()
