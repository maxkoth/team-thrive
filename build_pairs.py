#!/usr/bin/env python3
"""Rebuild feature slides as 2-up pairs (two phones side by side) to cut page count.
New carousel: 01 cover | 02-06 five paired feature slides | 07 comparison | 08 closing."""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NAVY  = (13, 27, 62)
GREEN = (61, 220, 132)
WHITE = (255, 255, 255)
MUTE  = (156, 174, 208)
SCREEN_BG = (5, 8, 15)

FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
BOLD = os.path.join(FONT_DIR, "Outfit-Bold.ttf")
REG  = os.path.join(FONT_DIR, "Outfit-Regular.ttf")

SRC = "figma-assets/screens"
OUT = "instagram-carousel"
W = H = 1080
MARGIN = 80

def font(p, s): return ImageFont.truetype(p, s)
def tw(d, s, f): return d.textbbox((0,0), s, font=f)[2]
def th(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[3]-b[1]

LOGO = Image.open("figma-assets/logo_teamthrive_mark.png").convert("RGBA")

def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,size[0]-1,size[1]-1], radius, fill=255)
    return m

def phone_mockup(screen_img, sw, sh):
    bezel = 12; ro = 46; ri = 34
    pw, ph = sw + bezel*2, sh + bezel*2
    phone = Image.new("RGBA", (pw, ph), (0,0,0,0))
    body = Image.new("RGBA", (pw, ph), (0,0,0,0))
    ImageDraw.Draw(body).rounded_rectangle([0,0,pw-1,ph-1], ro, fill=SCREEN_BG+(255,))
    phone.alpha_composite(body)
    ImageDraw.Draw(phone).rounded_rectangle([0,0,pw-1,ph-1], ro, outline=(70,90,130,180), width=2)
    scr = screen_img.convert("RGBA").resize((sw, sh))
    scr.putalpha(rounded_mask((sw, sh), ri))
    phone.alpha_composite(scr, (bezel, bezel))
    return phone

def prep_screen(frame, tw_, th_):
    im = Image.open(f"{SRC}/frame_{frame:03d}.png").convert("RGB")
    scale = tw_ / im.width
    im = im.resize((tw_, round(im.height*scale)))
    return im.crop((0, 0, tw_, min(im.height, th_)))

def draw_logo(c, d):
    x, y = MARGIN, 50; h = 58
    w = round(LOGO.width * h / LOGO.height)
    c.alpha_composite(LOGO.resize((w, h)), (x, y))
    d.text((x + w + 18, y + (h - 31)//2 - 2), "Team Thrive", font=font(BOLD, 31), fill=WHITE)

def footer(d):
    ff = font(REG, 26)
    d.text(((W - tw(d, "teamthrive.com", ff))//2, 1022), "teamthrive.com", font=ff, fill=GREEN)

def build_pair(idx, eyebrow, left, right):
    canvas = Image.new("RGBA", (W, H), NAVY + (255,))
    d = ImageDraw.Draw(canvas)

    # soft green glow center
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    ImageDraw.Draw(glow).ellipse([W//2-320, 300, W//2+320, 900], fill=GREEN+(34,))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(100)))

    draw_logo(canvas, d)

    # eyebrow category label (centered, green)
    ef = font(BOLD, 28)
    d.text(((W - tw(d, eyebrow, ef))//2, 150), eyebrow, font=ef, fill=GREEN)

    # two phones side by side
    sw, sh = 234, 496
    phones = []
    for frame in (left[0], right[0]):
        scr = prep_screen(frame, sw, sh)
        phones.append(phone_mockup(scr, sw, sh))
    pw, ph = phones[0].size
    gap = 64
    total = pw*2 + gap
    x0 = (W - total)//2
    py = 224
    xs = [x0, x0 + pw + gap]

    for k, phone in enumerate(phones):
        px = xs[k]
        shadow = Image.new("RGBA", (W, H), (0,0,0,0))
        ImageDraw.Draw(shadow).rounded_rectangle([px, py+16, px+pw, py+ph+16], 46, fill=(0,0,0,140))
        canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)))
        canvas.alpha_composite(phone, (px, py))

    # captions under each phone
    cap_y = py + ph + 30
    for k, feat in enumerate((left, right)):
        _, name, desc = feat
        cx = xs[k] + pw//2
        nf = font(BOLD, 30)
        d.text((cx - tw(d, name, nf)//2, cap_y), name, font=nf, fill=WHITE)
        df = font(REG, 22)
        lines = textwrap.wrap(desc, width=26)
        ty = cap_y + 44
        for ln in lines:
            d.text((cx - tw(d, ln, df)//2, ty), ln, font=df, fill=MUTE)
            ty += 30

    footer(d)
    out = f"{OUT}/slide_{idx:02d}.png"
    canvas.convert("RGB").save(out, "PNG")
    return out

PAIRS = [
    ("STAY CONNECTED", (134, "Communication", "Team chats, announcements & updates in one place"),
                       (25,  "Scheduling", "Games, practices & RSVPs, always in sync")),
    ("KNOW YOUR TEAM", (28,  "Roster Management", "Add & manage players, coaches & staff fast"),
                       (92,  "Athlete Profiles", "Every athlete's info & progress at a glance")),
    ("RUN THE CLUB",   (122, "Payments", "Collect dues & send invoices effortlessly"),
                       (27,  "Team Dashboard", "Your whole team's activity in one view")),
    ("EVERYONE INCLUDED", (93, "Parent Portal", "Keep parents looped in with their athletes"),
                          (105,"Coach Tools", "Everything coaches need to lead with ease")),
    ("BUILT TO SCALE", (44,  "Club Management", "Run every team in your club from one app"),
                       (46,  "Smart Filters", "Find any event, team or athlete in seconds")),
]

for i, (eb, l, r) in enumerate(PAIRS, 2):   # slides 02..06
    print("built", build_pair(i, eb, l, r))
print("done")
