#!/usr/bin/env python3
"""3-column Phase 1 / Phase 2 / Phase 3 comparison — replaces slide_07."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NAVY  = (13, 27, 62)
GREEN = (61, 220, 132)
WHITE = (255, 255, 255)
MUTE  = (156, 174, 208)

FD = "/mnt/skills/examples/canvas-design/canvas-fonts"
BOLD = os.path.join(FD, "Outfit-Bold.ttf")
REG  = os.path.join(FD, "Outfit-Regular.ttf")
OUT = "instagram-carousel"
W = H = 1080
MARGIN = 50

def font(p, s): return ImageFont.truetype(p, s)
def tw(d, s, f): return d.textbbox((0,0), s, font=f)[2]
def th(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[3]-b[1]
def fit(d, s, path, start, maxw, minsz=30):
    sz = start
    while sz > minsz and tw(d, s, font(path, sz)) > maxw: sz -= 2
    return font(path, sz)
def uniform(d, items, path, start, maxw, minsz=15):
    sz = start
    while sz > minsz and any(tw(d, it, font(path, sz)) > maxw for it in items): sz -= 1
    return font(path, sz)

LOGO = Image.open("figma-assets/logo_teamthrive_mark.png").convert("RGBA")

def base(box=None, a=26, blur=115):
    c = Image.new("RGBA", (W, H), NAVY + (255,))
    if box:
        g = Image.new("RGBA", (W, H), (0,0,0,0))
        ImageDraw.Draw(g).ellipse(box, fill=GREEN + (a,))
        c.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))
    return c

def logo(c, d):
    x,y=MARGIN,46; h=54; w=round(LOGO.width*h/LOGO.height)
    c.alpha_composite(LOGO.resize((w,h)),(x,y))
    d.text((x+w+16,y+(h-30)//2-2),"Team Thrive",font=font(BOLD,30),fill=WHITE)

def footer(d):
    ff=font(REG,25); d.text(((W-tw(d,"teamthrive.com",ff))//2,1024),"teamthrive.com",font=ff,fill=GREEN)

def badge(kind, size=30):
    b=Image.new("RGBA",(size,size),(0,0,0,0)); dd=ImageDraw.Draw(b); s=size
    dd.rounded_rectangle([0,0,s-1,s-1],s//3,fill=GREEN)
    if kind=="check":
        dd.line([(s*0.26,s*0.52),(s*0.43,s*0.69)],fill=NAVY,width=4,joint="curve")
        dd.line([(s*0.43,s*0.69),(s*0.76,s*0.31)],fill=NAVY,width=4,joint="curve")
    elif kind=="arrow":
        dd.line([(s*0.26,s*0.5),(s*0.70,s*0.5)],fill=NAVY,width=4,joint="curve")
        dd.line([(s*0.55,s*0.33),(s*0.72,s*0.5)],fill=NAVY,width=4,joint="curve")
        dd.line([(s*0.55,s*0.67),(s*0.72,s*0.5)],fill=NAVY,width=4,joint="curve")
    else:  # star / sparkle
        import math
        cx,cy,ro,ri=s/2,s/2,s*0.30,s*0.13; pts=[]
        for i in range(10):
            ang=-math.pi/2+i*math.pi/5; r=ro if i%2==0 else ri
            pts.append((cx+r*math.cos(ang),cy+r*math.sin(ang)))
        dd.polygon(pts,fill=NAVY)
    return b

def panel(canvas, x0, x1, y0, y1, accent):
    p=Image.new("RGBA",(x1-x0,y1-y0),(0,0,0,0)); dp=ImageDraw.Draw(p)
    dp.rounded_rectangle([0,0,x1-x0-1,y1-y0-1],28,fill=(255,255,255,10))
    dp.rounded_rectangle([0,0,x1-x0-1,y1-y0-1],28,outline=(61,220,132,110) if accent else (255,255,255,38),width=2)
    canvas.alpha_composite(p,(x0,y0))

def column(canvas, d, x0, x1, y0, y1, header, sub, filled, items, kind):
    cx=(x0+x1)//2
    hf=font(BOLD,27); hw=tw(d,header,hf); pad=20; pw=hw+pad*2
    px=cx-pw//2; py=y0+26
    pill=Image.new("RGBA",(pw,52),(0,0,0,0))
    if filled: ImageDraw.Draw(pill).rounded_rectangle([0,0,pw-1,51],26,fill=GREEN); tc=NAVY
    else: ImageDraw.Draw(pill).rounded_rectangle([0,0,pw-1,51],26,outline=GREEN,width=3); tc=GREEN
    canvas.alpha_composite(pill,(px,py))
    d.text((px+pad,py+26-th(d,header,hf)//2-3),header,font=hf,fill=tc)
    sf=font(REG,20); d.text((cx-tw(d,sub,sf)//2,py+60),sub,font=sf,fill=MUTE)

    pad_in=20; bsz=28; tx=x0+pad_in+bsz+11
    maxw=(x1-pad_in)-tx
    bf=uniform(d,items,REG,21,maxw,minsz=15)
    b=badge(kind,bsz)
    items_top=py+112; items_bot=y1-24
    pitch=(items_bot-items_top)/len(items)
    for k,it in enumerate(items):
        cy2=items_top+pitch*(k+0.5)
        canvas.alpha_composite(b,(x0+pad_in,int(cy2-bsz/2)))
        d.text((tx,int(cy2-th(d,it,bf)/2-2)),it,font=bf,fill=WHITE)

def build(idx):
    c=base([W//2-400,300,W//2+400,1060],a=22,blur=125); d=ImageDraw.Draw(c)
    logo(c,d)
    title="Now. Next. Beyond."
    tf=fit(d,title,BOLD,58,W-MARGIN*2)
    d.text(((W-tw(d,title,tf))//2,150),title,font=tf,fill=WHITE)
    sub="Everything live today — and where Team Thrive is headed"
    sf=fit(d,sub,REG,26,W-MARGIN*2); d.text(((W-tw(d,sub,sf))//2,222),sub,font=sf,fill=MUTE)

    y0,y1=290,1000
    gap=20; colw=(W-MARGIN*2-gap*2)//3
    xs=[MARGIN, MARGIN+colw+gap, MARGIN+2*(colw+gap)]
    for i in range(3):
        panel(c, xs[i], xs[i]+colw, y0, y1, accent=(i==2))
    column(c,d,xs[0],xs[0]+colw,y0,y1,"PHASE 1","Live now",True,[
        "Team communication","Roster management","Scheduling & events",
        "Payments & invoicing","Athlete profiles","Club management",
    ],"check")
    column(c,d,xs[1],xs[1]+colw,y0,y1,"PHASE 2","Coming soon",False,[
        "Club concept & coaches","Multi-team events","Deep-link invites",
        "Open parent sign-up","Athletes 13+ access","Fresh new design",
    ],"arrow")
    column(c,d,xs[2],xs[2]+colw,y0,y1,"PHASE 3","On the roadmap",False,[
        "Athlete Journey timeline","Lifelong sports history","AI video feedback",
        "Coach & parent notes","Video storage (Premium)","Starter & Pro plans",
    ],"star")
    footer(d)
    out=f"{OUT}/slide_{idx:02d}.png"; c.convert("RGB").save(out); return out

print("built", build(7))
