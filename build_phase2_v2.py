#!/usr/bin/env python3
"""Condensed Phase 2: a side-by-side Phase 1 vs Phase 2 comparison + closing.
Replaces the earlier 6-slide roadmap (slides 11-16) with 2 slides (11-12)."""
import os, glob, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NAVY  = (13, 27, 62)
GREEN = (61, 220, 132)
WHITE = (255, 255, 255)
MUTE  = (150, 170, 205)

FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
BOLD = os.path.join(FONT_DIR, "Outfit-Bold.ttf")
REG  = os.path.join(FONT_DIR, "Outfit-Regular.ttf")

OUT = "instagram-carousel"
W = H = 1080
MARGIN = 80

def font(p, s): return ImageFont.truetype(p, s)
def tw(d, s, f): return d.textbbox((0,0), s, font=f)[2]
def th(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[3]-b[1]
def fit_font(d, s, path, start, maxw, minsz=30):
    sz = start
    while sz > minsz and tw(d, s, font(path, sz)) > maxw: sz -= 2
    return font(path, sz)

LOGO = Image.open("figma-assets/logo_teamthrive_mark.png").convert("RGBA")

def base_canvas(box=None, a=44, blur=95):
    c = Image.new("RGBA", (W, H), NAVY + (255,))
    if box:
        g = Image.new("RGBA", (W, H), (0,0,0,0))
        ImageDraw.Draw(g).ellipse(box, fill=GREEN + (a,))
        c.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))
    return c

def draw_logo(c, d):
    x, y = MARGIN, 52; h = 60
    w = round(LOGO.width * h / LOGO.height)
    c.alpha_composite(LOGO.resize((w, h)), (x, y))
    d.text((x + w + 18, y + (h - 32)//2 - 2), "Team Thrive", font=font(BOLD, 32), fill=WHITE)

def footer(d):
    ff = font(REG, 26)
    d.text(((W - tw(d, "teamthrive.com", ff))//2, 1020), "teamthrive.com", font=ff, fill=GREEN)

def icon_badge(kind, size=40):
    b = Image.new("RGBA", (size, size), (0,0,0,0))
    dd = ImageDraw.Draw(b); s = size
    dd.rounded_rectangle([0,0,s-1,s-1], s//3, fill=GREEN)
    if kind == "check":
        dd.line([(s*0.26,s*0.52),(s*0.43,s*0.69)], fill=NAVY, width=5, joint="curve")
        dd.line([(s*0.43,s*0.69),(s*0.76,s*0.31)], fill=NAVY, width=5, joint="curve")
    else:  # arrow
        dd.line([(s*0.28,s*0.5),(s*0.68,s*0.5)], fill=NAVY, width=5, joint="curve")
        dd.line([(s*0.54,s*0.34),(s*0.70,s*0.5)], fill=NAVY, width=5, joint="curve")
        dd.line([(s*0.54,s*0.66),(s*0.70,s*0.5)], fill=NAVY, width=5, joint="curve")
    return b

def draw_column(canvas, d, x0, x1, top, header, sub, pill_fill, items, kind):
    # header pill
    hf = font(BOLD, 30)
    hw = tw(d, header, hf); pad = 26
    pill_w = hw + pad*2
    px = x0 + ((x1 - x0) - pill_w)//2
    pill = Image.new("RGBA", (pill_w, 58), (0,0,0,0))
    if pill_fill:
        ImageDraw.Draw(pill).rounded_rectangle([0,0,pill_w-1,57], 29, fill=GREEN)
        tcol = NAVY
    else:
        ImageDraw.Draw(pill).rounded_rectangle([0,0,pill_w-1,57], 29, outline=GREEN, width=3)
        tcol = GREEN
    canvas.alpha_composite(pill, (px, top))
    d.text((px + pad, top + 29 - th(d, header, hf)//2 - 3), header, font=hf, fill=tcol)
    # sub label
    sf = font(REG, 24)
    d.text((x0 + ((x1-x0) - tw(d, sub, sf))//2, top + 66), sub, font=sf, fill=MUTE)

    # items
    badge = icon_badge(kind, 40)
    bf = font(REG, 27)
    y = top + 120
    line_h = 34
    text_x = x0 + 40 + 16
    text_w_chars = 20
    for it in items:
        lines = textwrap.wrap(it, width=text_w_chars)
        row_h = max(40, len(lines)*line_h)
        canvas.alpha_composite(badge, (x0, y + (row_h - 40)//2))
        ty = y + (row_h - len(lines)*line_h)//2
        for ln in lines:
            d.text((text_x, ty), ln, font=bf, fill=WHITE); ty += line_h
        y += row_h + 22

# ── Slide 11: side-by-side comparison ────────────────────────────────────
def build_compare(idx):
    canvas = base_canvas([W//2-360, 300, W//2+360, 1050], a=30, blur=110)
    d = ImageDraw.Draw(canvas)
    draw_logo(canvas, d)

    title = "Here now. Coming next."
    tf = fit_font(d, title, BOLD, 64, W - MARGIN*2)
    d.text(((W - tw(d, title, tf))//2, 168), title, font=tf, fill=WHITE)

    # center divider
    d.line([(W//2, 300), (W//2, 980)], fill=(255,255,255,40), width=2)

    top = 310
    draw_column(canvas, d, MARGIN, W//2 - 24, top,
                "PHASE 1", "Live in the app now", True, [
                    "Team chat & announcements",
                    "Roster management",
                    "Scheduling & RSVPs",
                    "Payments & invoicing",
                    "Athlete profiles",
                    "Coach & club tools",
                ], "check")
    draw_column(canvas, d, W//2 + 24, W - MARGIN, top,
                "PHASE 2", "Coming next", False, [
                    "Club concept & coach management",
                    "Move athletes between teams",
                    "Multi-team events",
                    "Deep-link invites & open sign-up",
                    "Athletes 13+ & parent roles",
                    "Multi-sport profiles & fresh design",
                ], "arrow")
    footer(d)
    out = f"{OUT}/slide_{idx:02d}.png"
    canvas.convert("RGB").save(out, "PNG")
    return out

# ── Slide 12: closing ────────────────────────────────────────────────────
def build_closing(idx):
    canvas = base_canvas([W//2-340, 120, W//2+340, 760], a=50, blur=110)
    d = ImageDraw.Draw(canvas)
    lh = 188
    lw = round(LOGO.width * lh / LOGO.height)
    canvas.alpha_composite(LOGO.resize((lw, lh)), ((W - lw)//2, 170))
    d.text(((W - tw(d, "TEAM THRIVE", font(BOLD, 50)))//2, 170 + lh + 18),
           "TEAM THRIVE", font=font(BOLD, 50), fill=WHITE)
    for i, ln in enumerate(["The best is", "yet to come"]):
        d.text(((W - tw(d, ln, font(BOLD, 88)))//2, 570 + i*98), ln, font=font(BOLD, 88), fill=WHITE)
    sub = "Download Team Thrive and grow with us."
    d.text(((W - tw(d, sub, font(REG, 36)))//2, 570 + 2*98 + 16), sub, font=font(REG, 36), fill=GREEN)
    footer(d)
    out = f"{OUT}/slide_{idx:02d}.png"
    canvas.convert("RGB").save(out, "PNG")
    return out

# remove the old 6-slide roadmap (11-16)
for f in glob.glob(f"{OUT}/slide_1[1-6].png"):
    os.remove(f); print("removed", f)

print("built", build_compare(11))
print("built", build_closing(12))
print("done")
