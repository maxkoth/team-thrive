#!/usr/bin/env python3
"""Motion-graphics engine for Team Thrive Reels. Renders frames with PIL, encodes mp4."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio

NAVY=(13,27,62); GREEN=(61,220,132); WHITE=(255,255,255); SCREEN_BG=(5,8,15)
SUB=(190,200,218)
FD="/mnt/skills/examples/canvas-design/canvas-fonts"
BOLD=os.path.join(FD,"Outfit-Bold.ttf"); REG=os.path.join(FD,"Outfit-Regular.ttf")
LOGO=Image.open("figma-assets/logo_teamthrive_mark.png").convert("RGBA")
SRC="figma-assets/screens"
W,H=1080,1920; FPS=30

def font(p,s): return ImageFont.truetype(p,s)
def clamp01(x): return 0.0 if x<0 else 1.0 if x>1 else x
def seg(t,a,b): return clamp01((t-a)/(b-a)) if b>a else (1.0 if t>=b else 0.0)
def ease_out(t): return 1-(1-t)**3
def ease_io(t): return t*t*(3-2*t)
def ease_back(t):  # slight overshoot
    c=1.70158; return 1+ (c+1)*(t-1)**3 + c*(t-1)**2
def lerp(a,b,t): return a+(b-a)*t

# ---- precompute background (navy + soft green glow) ----
def make_bg(cy):
    bg=Image.new("RGB",(W,H),NAVY)
    g=Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(g).ellipse([W//2-460,cy-460,W//2+460,cy+460],fill=GREEN+(40,))
    bg=Image.alpha_composite(bg.convert("RGBA"),g.filter(ImageFilter.GaussianBlur(140))).convert("RGB")
    return bg
BG_MID=make_bg(960)

def text_layer(text,fnt,fill):
    d=ImageDraw.Draw(Image.new("RGB",(2,2)))
    b=d.textbbox((0,0),text,font=fnt)
    im=Image.new("RGBA",(b[2]-b[0]+8,b[3]-b[1]+8),(0,0,0,0))
    ImageDraw.Draw(im).text((4-b[0],4-b[1]),text,font=fnt,fill=fill)
    return im

def paste_alpha(base,layer,xy,alpha=1.0,scale=1.0):
    if scale!=1.0:
        layer=layer.resize((max(1,int(layer.width*scale)),max(1,int(layer.height*scale))),Image.LANCZOS)
    if alpha<1.0:
        a=layer.split()[3].point(lambda p:int(p*alpha)); layer=layer.copy(); layer.putalpha(a)
    base.alpha_composite(layer,(int(xy[0]),int(xy[1])))

def center_x(layer): return (W-layer.width)//2

# ---- phone parts ----
SW,SH=466,1009; BEZEL=14; RO=58; RI=44
PW,PH=SW+BEZEL*2,SH+BEZEL*2
def make_body():
    b=Image.new("RGBA",(PW,PH),(0,0,0,0))
    ImageDraw.Draw(b).rounded_rectangle([0,0,PW-1,PH-1],RO,fill=SCREEN_BG+(255,))
    ImageDraw.Draw(b).rounded_rectangle([0,0,PW-1,PH-1],RO,outline=(70,90,130,220),width=3)
    return b
BODY=make_body()
SMASK=Image.new("L",(SW,SH),0); ImageDraw.Draw(SMASK).rounded_rectangle([0,0,SW-1,SH-1],RI,fill=255)

def prep_screen(frame):
    im=Image.open(f"{SRC}/frame_{frame:03d}.png").convert("RGB")
    s=SW/im.width; im=im.resize((SW,round(im.height*s)))
    return im.crop((0,0,SW,min(im.height,SH)))

def phone_with_screen(screen_layer):
    """screen_layer: RGBA size (SW,SH). Returns full phone RGBA."""
    ph=BODY.copy()
    sc=screen_layer.copy(); sc.putalpha(SMASK)
    ph.alpha_composite(sc,(BEZEL,BEZEL))
    return ph

def screen_swipe(scrA,scrB,prog):
    """prog 0->1 slides A out left, B in from right. RGB inputs -> RGBA layer."""
    lay=Image.new("RGBA",(SW,SH),(0,0,0,0))
    off=int(prog*SW)
    lay.paste(scrA,(-off,0)); lay.paste(scrB,(SW-off,0))
    return lay

def shadow_for(px,py,pw,ph):
    s=Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(s).rounded_rectangle([px,py+22,px+pw,py+ph+22],RO,fill=(0,0,0,150))
    return s.filter(ImageFilter.GaussianBlur(30))

def draw_logo_mark(frame,cx,cy,h,alpha=1.0):
    w=round(LOGO.width*h/LOGO.height)
    paste_alpha(frame,LOGO,(cx-w//2,cy-h//2),alpha=alpha,scale=h/LOGO.height)

def logo_lockup_topleft(frame,alpha=1.0,y=70):
    h=64; w=round(LOGO.width*h/LOGO.height)
    paste_alpha(frame,LOGO,(70,y),alpha=alpha,scale=h/LOGO.height)
    tl=text_layer("Team Thrive",font(BOLD,38),WHITE)
    paste_alpha(frame,tl,(70+w+20,y+(h-tl.height)//2),alpha=alpha)
