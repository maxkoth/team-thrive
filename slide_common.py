"""Shared styling/helpers for Team Thrive Instagram carousels."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NAVY=(13,27,62); GREEN=(61,220,132); WHITE=(255,255,255); SCREEN_BG=(5,8,15)
GREEN_DK=(38,150,92)
W=H=1080; MARGIN=80

FD="/mnt/skills/examples/canvas-design/canvas-fonts"
BOLD=os.path.join(FD,"Outfit-Bold.ttf"); REG=os.path.join(FD,"Outfit-Regular.ttf")
SRC="figma-assets/screens"
LOGO=Image.open("figma-assets/logo_teamthrive_mark.png").convert("RGBA")

def font(p,s): return ImageFont.truetype(p,s)
def tw(d,s,f): return d.textbbox((0,0),s,font=f)[2]-d.textbbox((0,0),s,font=f)[0]
def fit(d,s,p,start,maxw,minsz=34):
    sz=start
    while sz>minsz and tw(d,s,font(p,sz))>maxw: sz-=2
    return font(p,sz)
def centered(d,s,y,f,fill):
    d.text(((W-tw(d,s,f))//2,y),s,font=f,fill=fill)

def rounded_mask(size,r):
    m=Image.new("L",size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,size[0]-1,size[1]-1],r,fill=255); return m

def new_canvas(glow_box=(W//2-280,430,W//2+280,1010)):
    c=Image.new("RGBA",(W,H),NAVY+(255,))
    g=Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(g).ellipse(list(glow_box),fill=GREEN+(46,))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(95)))
    return c

def draw_logo(canvas,d,y=52,h=66):
    w=round(LOGO.width*h/LOGO.height)
    canvas.alpha_composite(LOGO.resize((w,h)),(MARGIN,y))
    d.text((MARGIN+w+20,y+(h-36)//2-2),"Team Thrive",font=font(BOLD,36),fill=WHITE)

def footer(canvas,d,txt="teamthrive.com",y=1018):
    centered(d,txt,y,font(REG,26),GREEN)

def phone_mockup(screen_img,sw,sh):
    bezel=14; ro=54; ri=40
    pw,ph=sw+bezel*2,sh+bezel*2
    phone=Image.new("RGBA",(pw,ph),(0,0,0,0))
    ImageDraw.Draw(phone).rounded_rectangle([0,0,pw-1,ph-1],ro,fill=SCREEN_BG+(255,))
    ImageDraw.Draw(phone).rounded_rectangle([0,0,pw-1,ph-1],ro,outline=(70,90,130,180),width=2)
    scr=screen_img.convert("RGBA").resize((sw,sh)); scr.putalpha(rounded_mask((sw,sh),ri))
    phone.alpha_composite(scr,(bezel,bezel))
    return phone

def prep_screen(frame,tw_,th_):
    im=Image.open(f"{SRC}/frame_{frame:03d}.png").convert("RGB")
    s=tw_/im.width; im=im.resize((tw_,round(im.height*s)))
    return im.crop((0,0,tw_,min(im.height,th_)))

def place_phone(canvas,frame,top,sw=300,sh=600):
    scr=prep_screen(frame,sw,sh)
    phone=phone_mockup(scr,sw,sh); pw,ph=phone.size; px=(W-pw)//2
    sh_img=Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(sh_img).rounded_rectangle([px,top+18,px+pw,top+ph+18],54,fill=(0,0,0,150))
    canvas.alpha_composite(sh_img.filter(ImageFilter.GaussianBlur(26)))
    canvas.alpha_composite(phone,(px,top))

def save(canvas,path):
    canvas.convert("RGB").save(path,"PNG"); return path
