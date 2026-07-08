#!/usr/bin/env python3
"""Phase 2 — polished side-by-side Phase 1 vs Phase 2 comparison + closing (slides 11-12)."""
import os, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NAVY  = (13, 27, 62)
GREEN = (61, 220, 132)
WHITE = (255, 255, 255)
MUTE  = (156, 174, 208)

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
def uniform_font(d, items, path, start, maxw, minsz=20):
    """Largest size (<=start) at which every item fits on one line."""
    sz = start
    while sz > minsz and any(tw(d, it, font(path, sz)) > maxw for it in items): sz -= 1
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
    x, y = MARGIN, 50; h = 58
    w = round(LOGO.width * h / LOGO.height)
    c.alpha_composite(LOGO.resize((w, h)), (x, y))
    d.text((x + w + 18, y + (h - 31)//2 - 2), "Team Thrive", font=font(BOLD, 31), fill=WHITE)

def footer(d):
    ff = font(REG, 26)
    d.text(((W - tw(d, "teamthrive.com", ff))//2, 1022), "teamthrive.com", font=ff, fill=GREEN)

def icon_badge(kind, size=36):
    b = Image.new("RGBA", (size, size), (0,0,0,0))
    dd = ImageDraw.Draw(b); s = size
    dd.rounded_rectangle([0,0,s-1,s-1], s//3, fill=GREEN)
    if kind == "check":
        dd.line([(s*0.26,s*0.52),(s*0.43,s*0.69)], fill=NAVY, width=5, joint="curve")
        dd.line([(s*0.43,s*0.69),(s*0.76,s*0.31)], fill=NAVY, width=5, joint="curve")
    else:
        dd.line([(s*0.26,s*0.5),(s*0.70,s*0.5)], fill=NAVY, width=5, joint="curve")
        dd.line([(s*0.55,s*0.33),(s*0.72,s*0.5)], fill=NAVY, width=5, joint="curve")
        dd.line([(s*0.55,s*0.67),(s*0.72,s*0.5)], fill=NAVY, width=5, joint="curve")
    return b

def panel(canvas, x0, x1, y0, y1, accent):
    p = Image.new("RGBA", (x1-x0, y1-y0), (0,0,0,0))
    dp = ImageDraw.Draw(p)
    dp.rounded_rectangle([0,0,x1-x0-1,y1-y0-1], 34, fill=(255,255,255,10))
    border = (61,220,132,120) if accent else (255,255,255,40)
    dp.rounded_rectangle([0,0,x1-x0-1,y1-y0-1], 34, outline=border, width=2)
    canvas.alpha_composite(p, (x0, y0))

def draw_column(canvas, d, x0, x1, y0, y1, header, sub, filled, items, kind):
    cx = (x0 + x1)//2
    # header pill
    hf = font(BOLD, 32)
    hw = tw(d, header, hf); pad = 28; pw = hw + pad*2
    px = cx - pw//2; py = y0 + 34
    pill = Image.new("RGBA", (pw, 60), (0,0,0,0))
    if filled:
        ImageDraw.Draw(pill).rounded_rectangle([0,0,pw-1,59], 30, fill=GREEN); tcol = NAVY
    else:
        ImageDraw.Draw(pill).rounded_rectangle([0,0,pw-1,59], 30, outline=GREEN, width=3); tcol = GREEN
    canvas.alpha_composite(pill, (px, py))
    d.text((px + pad, py + 30 - th(d, header, hf)//2 - 3), header, font=hf, fill=tcol)
    # sub label
    sf = font(REG, 24)
    d.text((cx - tw(d, sub, sf)//2, py + 74), sub, font=sf, fill=MUTE)

    # items — uniform single-line font, evenly distributed
    pad_in = 34
    badge_sz = 36
    tx = x0 + pad_in + badge_sz + 18
    maxw = x1 - pad_in - tx + x0  # available text width
    maxw = (x1 - pad_in) - tx
    bf = uniform_font(d, items, REG, 27, maxw, minsz=20)
    items_top = py + 132
    items_bot = y1 - 34
    pitch = (items_bot - items_top) / len(items)
    badge = icon_badge(kind, badge_sz)
    for k, it in enumerate(items):
        cy = items_top + pitch*(k + 0.5)
        canvas.alpha_composite(badge, (x0 + pad_in, int(cy - badge_sz/2)))
        d.text((tx, int(cy - th(d, it, bf)/2 - 2)), it, font=bf, fill=WHITE)

def build_compare(idx):
    canvas = base_canvas([W//2-380, 260, W//2+380, 1060], a=26, blur=120)
    d = ImageDraw.Draw(canvas)
    draw_logo(canvas, d)

    title = "Here now. Coming next."
    tf = fit_font(d, title, BOLD, 60, W - MARGIN*2)
    d.text(((W - tw(d, title, tf))//2, 158), title, font=tf, fill=WHITE)
    sub = "Everything live today — plus what's on the way"
    sf = font(REG, 27)
    d.text(((W - tw(d, sub, sf))//2, 226), sub, font=sf, fill=MUTE)

    py0, py1 = 292, 1000
    gap = 30
    lx0, lx1 = MARGIN, W//2 - gap//2
    rx0, rx1 = W//2 + gap//2, W - MARGIN
    panel(canvas, lx0, lx1, py0, py1, accent=False)
    panel(canvas, rx0, rx1, py0, py1, accent=True)

    draw_column(canvas, d, lx0, lx1, py0, py1, "PHASE 1", "Live now", True, [
        "Team communication",
        "Roster management",
        "Scheduling & events",
        "Payments & invoicing",
        "Athlete profiles",
        "Parent portal",
        "Team dashboard",
        "Coach tools",
        "Club management",
    ], "check")
    draw_column(canvas, d, rx0, rx1, py0, py1, "PHASE 2", "Coming soon", False, [
        "Club concept & coaches",
        "Move athletes between teams",
        "Multi-team events",
        "Deep-link invites",
        "Open parent sign-up",
        "Athletes 13+ access",
        "Responsible-parent role",
        "Multi-sport profiles",
        "A fresh new design",
    ], "arrow")
    footer(d)
    out = f"{OUT}/slide_{idx:02d}.png"
    canvas.convert("RGB").save(out, "PNG")
    return out

def build_closing(idx):
    canvas = base_canvas([W//2-340, 130, W//2+340, 770], a=50, blur=115)
    d = ImageDraw.Draw(canvas)
    lh = 184
    lw = round(LOGO.width * lh / LOGO.height)
    canvas.alpha_composite(LOGO.resize((lw, lh)), ((W - lw)//2, 176))
    d.text(((W - tw(d, "TEAM THRIVE", font(BOLD, 48)))//2, 176 + lh + 20),
           "TEAM THRIVE", font=font(BOLD, 48), fill=WHITE)
    for i, ln in enumerate(["The best is", "yet to come"]):
        d.text(((W - tw(d, ln, font(BOLD, 86)))//2, 566 + i*96), ln, font=font(BOLD, 86), fill=WHITE)
    sub = "Download Team Thrive and grow with us."
    d.text(((W - tw(d, sub, font(REG, 34)))//2, 566 + 2*96 + 20), sub, font=font(REG, 34), fill=GREEN)
    footer(d)
    out = f"{OUT}/slide_{idx:02d}.png"
    canvas.convert("RGB").save(out, "PNG")
    return out

for f in glob.glob(f"{OUT}/slide_1[1-6].png"):
    os.remove(f)
print("built", build_compare(11))
print("built", build_closing(12))
print("done")
