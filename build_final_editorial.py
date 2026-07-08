#!/usr/bin/env python3
"""Full carousel in Draft 2 (Editorial) style.
01 cover | 02-06 editorial paired feature slides | 07 comparison | 08 closing."""
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
SRC = "figma-assets/screens"
OUT = "instagram-carousel"
W = H = 1080
MARGIN = 80

def font(p, s): return ImageFont.truetype(p, s)
def tw(d, s, f): return d.textbbox((0,0), s, font=f)[2]
def th(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[3]-b[1]
def fit(d, s, path, start, maxw, minsz=40):
    sz = start
    while sz > minsz and tw(d, s, font(path, sz)) > maxw: sz -= 2
    return font(path, sz)

LOGO = Image.open("figma-assets/logo_teamthrive_mark.png").convert("RGBA")

def rmask(size, r):
    m = Image.new("L", size, 0); ImageDraw.Draw(m).rounded_rectangle([0,0,size[0]-1,size[1]-1], r, fill=255); return m

def phone(frame, sw, sh, bezel=12, ro=46, ri=34):
    im = Image.open(f"{SRC}/frame_{frame:03d}.png").convert("RGB")
    sc = sw/im.width; im = im.resize((sw, round(im.height*sc))).crop((0,0,sw,min(round(im.height*sc),sh)))
    pw, ph = sw+bezel*2, sh+bezel*2
    p = Image.new("RGBA",(pw,ph),(0,0,0,0))
    b = Image.new("RGBA",(pw,ph),(0,0,0,0)); ImageDraw.Draw(b).rounded_rectangle([0,0,pw-1,ph-1],ro,fill=SCREEN_BG+(255,)); p.alpha_composite(b)
    ImageDraw.Draw(p).rounded_rectangle([0,0,pw-1,ph-1],ro,outline=(70,90,130,180),width=2)
    scr = im.convert("RGBA").resize((sw,sh)); scr.putalpha(rmask((sw,sh),ri)); p.alpha_composite(scr,(bezel,bezel))
    return p

def logo(c, d):
    x,y=MARGIN,50; h=58; w=round(LOGO.width*h/LOGO.height)
    c.alpha_composite(LOGO.resize((w,h)),(x,y))
    d.text((x+w+18,y+(h-31)//2-2),"Team Thrive",font=font(BOLD,31),fill=WHITE)

def footer(d):
    ff=font(REG,26); d.text(((W-tw(d,"teamthrive.com",ff))//2,1022),"teamthrive.com",font=ff,fill=GREEN)

def shadow(c, box, r=46, blur=24, a=140):
    s=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(s).rounded_rectangle(box,r,fill=(0,0,0,a)); c.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))

def build_pair(idx, headline, left, right):
    c=Image.new("RGBA",(W,H),NAVY2+(255,)); d=ImageDraw.Draw(c)
    gl=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(gl).ellipse([W-560,-120,W+200,560],fill=GREEN+(30,)); c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(120)))
    logo(c,d)
    hf=fit(d,headline,BOLD,72,W-MARGIN*2,minsz=48)
    d.text((MARGIN,150),headline,font=hf,fill=WHITE)
    d.rounded_rectangle([MARGIN,150+th(d,headline,hf)+30,MARGIN+96,150+th(d,headline,hf)+38],4,fill=GREEN)
    sw,sh=246,516; pL=phone(left[0],sw,sh); pR=phone(right[0],sw,sh); pw,phh=pL.size
    gap=48; x0=(W-(pw*2+gap))//2; xs=[x0,x0+pw+gap]; ys=[300,352]
    for k,(p,yy) in enumerate(zip((pL,pR),ys)):
        shadow(c,[xs[k],yy+18,xs[k]+pw,yy+phh+18]); c.alpha_composite(p,(xs[k],yy))
    for k,feat in enumerate((left,right)):
        cx=xs[k]+pw//2; yy=ys[k]+phh+22
        nf=font(BOLD,29); d.text((cx-tw(d,feat[1],nf)//2,yy),feat[1],font=nf,fill=GREEN)
        df=font(REG,20); ty=yy+40
        for ln in textwrap.wrap(feat[2],width=28):
            d.text((cx-tw(d,ln,df)//2,ty),ln,font=df,fill=MUTE); ty+=26
    footer(d)
    out=f"{OUT}/slide_{idx:02d}.png"; c.convert("RGB").save(out); return out

PAIRS = [
    ("STAY CONNECTED",  (134,"Communication","Team chats & announcements in one place"),
                        (25, "Scheduling","Games, practices & RSVPs in sync")),
    ("KNOW YOUR TEAM",  (55, "Team Roster","Players, positions & status at a glance"),
                        (52, "Event Details","See who's attending every game")),
    ("RUN THE CLUB",    (79, "Payments","Collect dues & send invoices with ease"),
                        (86, "Team Home","Your whole team's hub in one view")),
    ("EVERYONE INCLUDED",(93,"Parent Access","Keep parents looped in with their athletes"),
                        (68, "Easy Onboarding","Add members & staff in seconds")),
    ("BUILT TO SCALE",  (44, "Club Management","Run every team in your club from one app"),
                        (46, "Smart Filters","Find any event, team or athlete fast")),
]

for i,(hl,l,r) in enumerate(PAIRS, 2):
    print("built", build_pair(i, hl, l, r))
print("done")
