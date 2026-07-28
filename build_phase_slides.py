#!/usr/bin/env python3
"""Phase 2 & Phase 3 feature slides in the Editorial style (matches slides 02-06)."""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NAVY2 = (8, 16, 38)
GREEN = (61, 220, 132)
WHITE = (255, 255, 255)
MUTE  = (156, 174, 208)
SCREEN_BG = (5, 8, 15)

FD = "/mnt/skills/examples/canvas-design/canvas-fonts"
BOLD = os.path.join(FD, "Outfit-Bold.ttf")
REG  = os.path.join(FD, "Outfit-Regular.ttf")
OUT = "instagram-carousel"
W = H = 1080
MARGIN = 80

def F(p, s): return ImageFont.truetype(p, s)
def tw(d, s, f): return d.textbbox((0,0), s, font=f)[2]
def th(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[3]-b[1]
def fit(d, s, path, start, maxw, minsz=42):
    sz = start
    while sz > minsz and tw(d, s, F(path, sz)) > maxw: sz -= 2
    return F(path, sz)

LOGO = Image.open("figma-assets/logo_teamthrive_mark.png").convert("RGBA")

def rmask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,size[0]-1,size[1]-1], r, fill=255)
    return m

def phone_from(path, sw, sh, bezel=12, ro=46, ri=34):
    im = Image.open(path).convert("RGB")
    sc = sw/im.width
    im = im.resize((sw, round(im.height*sc))).crop((0, 0, sw, min(round(im.height*sc), sh)))
    pw, ph = sw+bezel*2, sh+bezel*2
    p = Image.new("RGBA", (pw, ph), (0,0,0,0))
    b = Image.new("RGBA", (pw, ph), (0,0,0,0))
    ImageDraw.Draw(b).rounded_rectangle([0,0,pw-1,ph-1], ro, fill=SCREEN_BG+(255,))
    p.alpha_composite(b)
    ImageDraw.Draw(p).rounded_rectangle([0,0,pw-1,ph-1], ro, outline=(70,90,130,180), width=2)
    scr = im.convert("RGBA").resize((sw, sh))
    scr.putalpha(rmask((sw, sh), ri))
    p.alpha_composite(scr, (bezel, bezel))
    return p

def logo(c, d):
    x, y = MARGIN, 50; h = 58
    w = round(LOGO.width*h/LOGO.height)
    c.alpha_composite(LOGO.resize((w, h)), (x, y))
    d.text((x+w+18, y+(h-31)//2-2), "Team Thrive", font=F(BOLD, 31), fill=WHITE)

def footer(d):
    ff = F(REG, 26)
    d.text(((W-tw(d,"teamthrive.com",ff))//2, 1022), "teamthrive.com", font=ff, fill=GREEN)

def shadow(c, box, r=46, blur=24, a=140):
    s = Image.new("RGBA", (W, H), (0,0,0,0))
    ImageDraw.Draw(s).rounded_rectangle(box, r, fill=(0,0,0,a))
    c.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))

def build(idx, eyebrow, headline, left, right):
    c = Image.new("RGBA", (W, H), NAVY2+(255,))
    d = ImageDraw.Draw(c)
    gl = Image.new("RGBA", (W, H), (0,0,0,0))
    ImageDraw.Draw(gl).ellipse([W-560, -120, W+200, 560], fill=GREEN+(30,))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(120)))
    logo(c, d)

    # eyebrow pill — marks this as upcoming, not live
    ef = F(BOLD, 22)
    ew = tw(d, eyebrow, ef); pad = 20
    d.rounded_rectangle([MARGIN, 140, MARGIN+ew+pad*2, 188], 24, outline=GREEN, width=3)
    d.text((MARGIN+pad, 154), eyebrow, font=ef, fill=GREEN)

    hf = fit(d, headline, BOLD, 72, W-MARGIN*2)
    d.text((MARGIN, 206), headline, font=hf, fill=WHITE)
    d.rounded_rectangle([MARGIN, 206+th(d,headline,hf)+28, MARGIN+96, 206+th(d,headline,hf)+36], 4, fill=GREEN)

    sw, sh = 246, 470
    pL = phone_from(left[0], sw, sh); pR = phone_from(right[0], sw, sh)
    pw, ph = pL.size
    gap = 48; x0 = (W-(pw*2+gap))//2
    xs = [x0, x0+pw+gap]; ys = [332, 380]
    for k, (p, yy) in enumerate(zip((pL, pR), ys)):
        shadow(c, [xs[k], yy+18, xs[k]+pw, yy+ph+18])
        c.alpha_composite(p, (xs[k], yy))
    for k, feat in enumerate((left, right)):
        cx = xs[k]+pw//2; yy = ys[k]+ph+20
        nf = F(BOLD, 29)
        d.text((cx-tw(d,feat[1],nf)//2, yy), feat[1], font=nf, fill=GREEN)
        df = F(REG, 20); ty = yy+40
        for ln in textwrap.wrap(feat[2], width=28):
            d.text((cx-tw(d,ln,df)//2, ty), ln, font=df, fill=MUTE); ty += 26
    footer(d)
    out = f"{OUT}/slide_{idx:02d}.png"
    c.convert("RGB").save(out); return out

print("built", build(7, "PHASE 2 · COMING SOON", "BUILT FOR CLUBS",
    ("concept/club.png", "Club Management", "Run every team, coach and roster under one club"),
    ("concept/invite.png", "Deep-Link Invites", "One link — parents and athletes join instantly")))

print("built", build(8, "PHASE 3 · ON THE ROADMAP", "THE ATHLETE JOURNEY",
    ("concept/journey.png", "Lifelong Journey", "Every team, position and milestone in one timeline"),
    ("concept/ai.png", "AI Video Feedback", "Upload a clip, get AI coaching feedback that lasts")))
print("done")
