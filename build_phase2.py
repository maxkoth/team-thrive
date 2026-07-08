#!/usr/bin/env python3
"""Append Team Thrive PHASE 2 roadmap slides to the Instagram carousel (1080x1080)."""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NAVY  = (13, 27, 62)     # #0D1B3E
GREEN = (61, 220, 132)   # #3DDC84
WHITE = (255, 255, 255)
MUTE  = (150, 170, 205)

FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
BOLD = os.path.join(FONT_DIR, "Outfit-Bold.ttf")
REG  = os.path.join(FONT_DIR, "Outfit-Regular.ttf")

OUT = "instagram-carousel"
os.makedirs(OUT, exist_ok=True)

W = H = 1080
MARGIN = 80

def font(path, size): return ImageFont.truetype(path, size)
def tw(d, s, f): return d.textbbox((0,0), s, font=f)[2]
def th(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[3]-b[1]

def fit_font(d, s, path, start, maxw, minsz=32):
    sz = start
    while sz > minsz and tw(d, s, font(path, sz)) > maxw: sz -= 2
    return font(path, sz)

LOGO = Image.open("figma-assets/logo_teamthrive_mark.png").convert("RGBA")

def base_canvas(glow_box=None, glow_alpha=46, blur=90):
    canvas = Image.new("RGBA", (W, H), NAVY + (255,))
    if glow_box:
        glow = Image.new("RGBA", (W, H), (0,0,0,0))
        ImageDraw.Draw(glow).ellipse(glow_box, fill=GREEN + (glow_alpha,))
        canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(blur)))
    return canvas

def draw_logo(canvas, d):
    x, y = MARGIN, 52
    h = 66
    w = round(LOGO.width * h / LOGO.height)
    canvas.alpha_composite(LOGO.resize((w, h)), (x, y))
    d.text((x + w + 20, y + (h - 36)//2 - 2), "Team Thrive", font=font(BOLD, 36), fill=WHITE)

def footer(d):
    ff = font(REG, 26)
    d.text(((W - tw(d, "teamthrive.com", ff))//2, 1018), "teamthrive.com", font=ff, fill=GREEN)

def check_badge(size=52):
    """Green rounded badge with a white check mark."""
    b = Image.new("RGBA", (size, size), (0,0,0,0))
    dd = ImageDraw.Draw(b)
    dd.rounded_rectangle([0, 0, size-1, size-1], size//3, fill=GREEN)
    # check mark
    s = size
    dd.line([(s*0.28, s*0.52), (s*0.44, s*0.68)], fill=NAVY, width=6, joint="curve")
    dd.line([(s*0.44, s*0.68), (s*0.74, s*0.34)], fill=NAVY, width=6, joint="curve")
    return b

# ── Slide 11: PHASE 2 divider ────────────────────────────────────────────
def build_divider(idx):
    canvas = base_canvas([W//2-360, 120, W//2+360, 780], glow_alpha=52, blur=115)
    d = ImageDraw.Draw(canvas)
    draw_logo(canvas, d)

    # small eyebrow pill "THE ROADMAP"
    eb = "THE ROADMAP"
    ef = font(BOLD, 30)
    ew = tw(d, eb, ef); pad = 30
    px0 = (W - (ew + pad*2))//2; py0 = 330
    pill = Image.new("RGBA", (ew + pad*2, 64), (0,0,0,0))
    ImageDraw.Draw(pill).rounded_rectangle([0,0,ew+pad*2-1,63], 32, outline=GREEN, width=3)
    canvas.alpha_composite(pill, (px0, py0))
    d.text((px0 + pad, py0 + 32 - th(d, eb, ef)//2 - 4), eb, font=ef, fill=GREEN)

    # huge "Phase 2"
    hf = font(BOLD, 200)
    d.text(((W - tw(d, "Phase 2", hf))//2, 420), "Phase 2", font=hf, fill=WHITE)

    # subtitle
    sub = "What's coming next to Team Thrive"
    sf = font(REG, 40)
    d.text(((W - tw(d, sub, sf))//2, 680), sub, font=sf, fill=GREEN)

    # swipe cue
    cue = "Swipe to see  →"
    cf = font(BOLD, 34)
    cw = tw(d, cue, cf); pad = 36
    px0 = (W - (cw + pad*2))//2; py0 = 862
    p2 = Image.new("RGBA", (cw + pad*2, 76), (0,0,0,0))
    ImageDraw.Draw(p2).rounded_rectangle([0,0,cw+pad*2-1,75], 38, fill=GREEN)
    canvas.alpha_composite(p2, (px0, py0))
    d.text((px0 + pad, py0 + 38 - th(d, cue, cf)//2 - 4), cue, font=cf, fill=NAVY)

    footer(d)
    out = f"{OUT}/slide_{idx:02d}.png"
    canvas.convert("RGB").save(out, "PNG")
    return out

# ── Roadmap checklist slides ─────────────────────────────────────────────
def build_roadmap(idx, title, items):
    canvas = base_canvas([W//2-320, 360, W//2+320, 1020], glow_alpha=34, blur=100)
    d = ImageDraw.Draw(canvas)
    draw_logo(canvas, d)

    # title (auto-fit, white)
    tf = fit_font(d, title, BOLD, 74, W - MARGIN*2)
    d.text(((W - tw(d, title, tf))//2, 190), title, font=tf, fill=WHITE)

    # accent underline
    uw = 90
    d.rounded_rectangle([(W-uw)//2, 190 + th(d, title, tf) + 40, (W+uw)//2, 190 + th(d, title, tf) + 48], 4, fill=GREEN)

    # checklist cards
    card_x0, card_x1 = MARGIN, W - MARGIN
    gap = 26
    badge_sz = 52
    body_font = font(REG, 34)
    line_h = 46
    badge = check_badge(badge_sz)

    # pre-measure each card height, then vertically center the whole stack
    cards = []
    for it in items:
        lines = textwrap.wrap(it, width=34)
        block_h = max(badge_sz + 40, len(lines)*line_h + 40)
        cards.append((lines, block_h))
    total_h = sum(bh for _, bh in cards) + gap*(len(cards)-1)
    region_top, region_bottom = 360, 980
    y = region_top + max(0, (region_bottom - region_top - total_h)//2)

    for lines, block_h in cards:
        # card background
        card = Image.new("RGBA", (card_x1-card_x0, block_h), (0,0,0,0))
        ImageDraw.Draw(card).rounded_rectangle([0,0,card_x1-card_x0-1,block_h-1], 28,
                                               fill=(255,255,255,12))
        ImageDraw.Draw(card).rounded_rectangle([0,0,card_x1-card_x0-1,block_h-1], 28,
                                               outline=(61,220,132,70), width=2)
        canvas.alpha_composite(card, (card_x0, y))
        # badge
        canvas.alpha_composite(badge, (card_x0 + 28, y + (block_h - badge_sz)//2))
        # text
        tx = card_x0 + 28 + badge_sz + 28
        ty = y + (block_h - len(lines)*line_h)//2 + 2
        for ln in lines:
            d.text((tx, ty), ln, font=body_font, fill=WHITE)
            ty += line_h
        y += block_h + gap

    footer(d)
    out = f"{OUT}/slide_{idx:02d}.png"
    canvas.convert("RGB").save(out, "PNG")
    return out

# ── Closing slide ────────────────────────────────────────────────────────
def build_closing(idx):
    canvas = base_canvas([W//2-340, 120, W//2+340, 760], glow_alpha=50, blur=110)
    d = ImageDraw.Draw(canvas)

    lh = 188
    lw = round(LOGO.width * lh / LOGO.height)
    canvas.alpha_composite(LOGO.resize((lw, lh)), ((W - lw)//2, 170))
    d.text(((W - tw(d, "TEAM THRIVE", font(BOLD, 50)))//2, 170 + lh + 18),
           "TEAM THRIVE", font=font(BOLD, 50), fill=WHITE)

    lines = ["The best is", "yet to come"]
    hf = font(BOLD, 88); y = 570
    for ln in lines:
        d.text(((W - tw(d, ln, hf))//2, y), ln, font=hf, fill=WHITE); y += 98

    sub = "Download Team Thrive and grow with us."
    sf = font(REG, 36)
    d.text(((W - tw(d, sub, sf))//2, y + 16), sub, font=sf, fill=GREEN)

    footer(d)
    out = f"{OUT}/slide_{idx:02d}.png"
    canvas.convert("RGB").save(out, "PNG")
    return out

# ── Content ──────────────────────────────────────────────────────────────
print("built", build_divider(11))
print("built", build_roadmap(12, "Smarter Club Management", [
    "A new club concept with easier coach management",
    "Move athletes between teams in the same club",
    "Invite multiple teams from one club to the same event",
]))
print("built", build_roadmap(13, "Effortless Onboarding", [
    "Deep-link invites — no more adding each parent by hand",
    "Parents can register anytime and be invited later",
]))
print("built", build_roadmap(14, "Built for Everyone", [
    "Athletes 13+ get their own app access",
    "A new responsible-parent role to support the coach",
    "Multi-sport profiles showing all current & former teams",
]))
print("built", build_roadmap(15, "A Fresh New Look", [
    "A refreshed visual style across the app",
    "New colors and a more modern, polished design",
]))
print("built", build_closing(16))
print("done")
