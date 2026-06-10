#!/usr/bin/env python3
"""Wrap the carousel slides in a mock Instagram post UI. One PNG per carousel position."""
import os, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NAVY=(13,27,62); GREEN=(61,220,132); TEAL=(45,217,195)
INK=(18,18,18); GRAY=(120,120,120); LINE=(219,219,219); BLUE=(0,149,246)
WHITE=(255,255,255); RED=(237,73,86)

FD="/mnt/skills/examples/canvas-design/canvas-fonts"
def F(b,s): return ImageFont.truetype(os.path.join(FD,b),s)
SEMI="Outfit-Bold.ttf"; REG="Outfit-Regular.ttf"

SLIDES=sorted(glob.glob("instagram-carousel/slide_*.png"))
N=len(SLIDES)
OUT="instagram-post"; os.makedirs(OUT,exist_ok=True)
LOGO=Image.open("figma-assets/logo_teamthrive_mark.png").convert("RGBA")

USER="teamthrive"
CAPTION=("Meet Team Thrive — the all-in-one app for youth sports clubs. "
         "Communication, rosters, scheduling, payments & more, in one place. "
         "Swipe to see it in action.  #youthsports #teammanagement #sportstech #coachlife")

W=1080
SS=4  # supersample icons for smooth edges

def icon(draw_fn, size, color, width):
    c=Image.new("RGBA",(size*SS,size*SS),(0,0,0,0))
    draw_fn(ImageDraw.Draw(c), size*SS, color, width*SS)
    return c.resize((size,size),Image.LANCZOS)

def i_heart(d,s,c,w):
    d.line([(s*.5,s*.86),(s*.14,s*.46)],fill=c,width=w)
    d.line([(s*.5,s*.86),(s*.86,s*.46)],fill=c,width=w)
    d.arc([s*.10,s*.16,s*.50,s*.56],180,360,fill=c,width=w)
    d.arc([s*.50,s*.16,s*.90,s*.56],180,360,fill=c,width=w)
def i_comment(d,s,c,w):
    d.arc([s*.12,s*.10,s*.88,s*.74],0,360,fill=c,width=w)  # approx round bubble
    d.line([(s*.30,s*.74),(s*.20,s*.90)],fill=c,width=w)
    d.line([(s*.20,s*.90),(s*.44,s*.72)],fill=c,width=w)
def i_share(d,s,c,w):
    d.line([(s*.08,s*.46),(s*.92,s*.12)],fill=c,width=w)
    d.line([(s*.92,s*.12),(s*.62,s*.92)],fill=c,width=w)
    d.line([(s*.62,s*.92),(s*.46,s*.56)],fill=c,width=w)
    d.line([(s*.46,s*.56),(s*.08,s*.46)],fill=c,width=w)
    d.line([(s*.46,s*.56),(s*.92,s*.12)],fill=c,width=w)
def i_bookmark(d,s,c,w):
    d.line([(s*.24,s*.10),(s*.76,s*.10)],fill=c,width=w)
    d.line([(s*.24,s*.10),(s*.24,s*.90)],fill=c,width=w)
    d.line([(s*.76,s*.10),(s*.76,s*.90)],fill=c,width=w)
    d.line([(s*.24,s*.90),(s*.50,s*.64)],fill=c,width=w)
    d.line([(s*.76,s*.90),(s*.50,s*.64)],fill=c,width=w)

HEART=icon(i_heart,56,INK,4)
COMMENT=icon(i_comment,56,INK,4)
SHARE=icon(i_share,56,INK,4)
BOOKMARK=icon(i_bookmark,56,INK,4)

def circle_avatar(diam):
    av=Image.new("RGBA",(diam,diam),(0,0,0,0))
    ImageDraw.Draw(av).ellipse([0,0,diam-1,diam-1],fill=NAVY)
    lh=int(diam*0.62); lw=round(LOGO.width*lh/LOGO.height)
    av.alpha_composite(LOGO.resize((lw,lh)),((diam-lw)//2,(diam-lh)//2))
    mask=Image.new("L",(diam,diam),0)
    ImageDraw.Draw(mask).ellipse([0,0,diam-1,diam-1],fill=255)
    av.putalpha(mask)
    return av

def wrap(d,text,fnt,maxw):
    words=text.split(); lines=[]; cur=""
    for wd in words:
        t=(cur+" "+wd).strip()
        if d.textlength(t,font=fnt)<=maxw: cur=t
        else: lines.append(cur); cur=wd
    if cur: lines.append(cur)
    return lines

AV=circle_avatar(84)
HEADER_H=132
ACTIONS_H=118

# precompute caption layout height
_tmp=ImageDraw.Draw(Image.new("RGB",(10,10)))
capf=F(REG,30); namef=F(SEMI,30)
name_w=_tmp.textlength(USER+" ",font=namef)
cap_lines=wrap(_tmp,CAPTION,capf,W-48-name_w) if False else None
# caption: bold username on first line, text flows after it with first-line indent
USER_W=int(_tmp.textlength(USER+"  ",font=F(SEMI,30)))
def layout_caption():
    words=CAPTION.split(); lines=[]; cur=""; first=True
    for wd in words:
        avail=(W-48-USER_W) if first else (W-48)
        t=(cur+" "+wd).strip()
        if _tmp.textlength(t,font=capf)<=avail: cur=t
        else: lines.append(cur); cur=wd; first=False
    if cur: lines.append(cur)
    return lines
cap_lines=layout_caption()
CAP_H=40+ len(cap_lines)*40 + 36+30+20  # likes + caption + meta

H=HEADER_H+W+ACTIONS_H+ int(CAP_H)
def build(idx, slide_path):
    img=Image.new("RGB",(W,H),WHITE)
    d=ImageDraw.Draw(img)
    # ---- header ----
    img.paste(AV,(28,(HEADER_H-84)//2),AV)
    tx=28+84+22
    d.text((tx,38),USER,font=F(SEMI,32),fill=INK)
    uw=d.textlength(USER,font=F(SEMI,32))
    # verified check
    cb=tx+uw+14; cy=54
    d.ellipse([cb,cy-13,cb+26,cy+13],fill=BLUE)
    d.line([(cb+7,cy),(cb+11,cy+5)],fill=WHITE,width=3)
    d.line([(cb+11,cy+5),(cb+19,cy-6)],fill=WHITE,width=3)
    d.text((tx,80),"Sponsored",font=F(REG,26),fill=GRAY)
    # three-dot menu
    for k in range(3):
        d.ellipse([W-58+k*0,0,0,0]) if False else None
    for k,dx in enumerate((-22,0,22)):
        d.ellipse([W-46+dx-4,HEADER_H//2-4,W-46+dx+4,HEADER_H//2+4],fill=INK)
    # ---- slide image ----
    sl=Image.open(slide_path).convert("RGB").resize((W,W))
    img.paste(sl,(0,HEADER_H))
    # carousel index pill
    pill=f"{idx}/{N}"; pf=F(SEMI,28)
    pw=d.textlength(pill,font=pf)
    px0=W-int(pw)-58; py0=HEADER_H+26
    pill_img=Image.new("RGBA",(int(pw)+36,46),(0,0,0,0))
    ImageDraw.Draw(pill_img).rounded_rectangle([0,0,int(pw)+35,45],22,fill=(0,0,0,150))
    img.paste(pill_img,(px0,py0),pill_img)
    d.text((px0+18,py0+8),pill,font=pf,fill=WHITE)
    # ---- actions ----
    ay=HEADER_H+W
    iy=ay+22
    def put(ic,x): img.paste(ic,(x,iy),ic)
    put(HEART,28); put(COMMENT,28+78); put(SHARE,28+156)
    put(BOOKMARK,W-28-56)
    # carousel dots (center)
    dot_y=iy+28; cxc=W//2; gap=26; r=6
    start=cxc-(N-1)*gap//2
    for k in range(N):
        col=BLUE if k==idx-1 else (200,200,200)
        rr= r if k==idx-1 else 5
        cx=start+k*gap
        d.ellipse([cx-rr,dot_y-rr,cx+rr,dot_y+rr],fill=col)
    # ---- likes + caption ----
    ty=ay+ACTIONS_H
    d.text((28,ty),"1,248 likes",font=F(SEMI,30),fill=INK)
    ty+=46
    d.text((28,ty),USER,font=F(SEMI,30),fill=INK)   # bold username
    for li,line in enumerate(cap_lines):
        x0=28+USER_W if li==0 else 28
        d.text((x0,ty),line,font=capf,fill=INK)
        ty+=40
    ty+=8
    d.text((28,ty),"View all 32 comments",font=F(REG,28),fill=GRAY); ty+=40
    d.text((28,ty),"2 HOURS AGO",font=F(REG,22),fill=GRAY)
    out=f"{OUT}/post_{idx:02d}.png"
    img.save(out)
    return out

for i,sp in enumerate(SLIDES,1):
    print("built",build(i,sp))
print("post size:",W,"x",H)
