#!/usr/bin/env python3
"""Carousel B — 'Outgrown the group chat?' problem->solution, numbered slides."""
import os
from PIL import ImageDraw
from slide_common import (W,H,MARGIN,NAVY,GREEN,WHITE,BOLD,REG,font,fit,centered,tw,
                          new_canvas,draw_logo,footer,place_phone,save,LOGO,ImageDraw as _)
from PIL import ImageDraw

OUT="carousel-b"; os.makedirs(OUT,exist_ok=True)

# (number, problem headline, green solution, frame)
ITEMS=[
    ("01","Updates get buried in chat","Every announcement, organized in one team feed.",134),
    ("02","Still chasing payments?","Automated dues, invoices & reminders.",122),
    ("03","Schedule changes = chaos","One live schedule everyone can see.",25),
    ("04","Rosters across 5 spreadsheets","One roster, always up to date.",28),
    ("05","Parents out of the loop","A portal that keeps every parent informed.",93),
]

def badge(canvas,d,num,cx,cy,r=46):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=GREEN)
    f=font(BOLD,46); b=d.textbbox((0,0),num,font=f)
    d.text((cx-(b[2]-b[0])/2,cy-(b[3]-b[1])/2-b[1]),num,font=f,fill=NAVY)

def cover(idx):
    c=new_canvas((W//2-340,120,W//2+340,720)); d=ImageDraw.Draw(c)
    draw_logo(c,d)
    centered(d,"5 signs you've",330,font(BOLD,78),WHITE)
    centered(d,"outgrown the",424,font(BOLD,78),WHITE)
    centered(d,"group chat",518,font(BOLD,78),GREEN)
    centered(d,"Is running your club harder than it should be?",648,font(REG,34),(190,200,218))
    # swipe pill
    cue="Swipe  →"; cf=font(BOLD,34); cw=tw(d,cue,cf); pad=36
    px=(W-(cw+pad*2))//2; py=820
    from PIL import Image as I
    pill=I.new("RGBA",(cw+pad*2,76),(0,0,0,0))
    ImageDraw.Draw(pill).rounded_rectangle([0,0,cw+pad*2-1,75],38,fill=GREEN)
    c.alpha_composite(pill,(px,py)); d.text((px+pad,py+20),cue,font=cf,fill=NAVY)
    footer(c,d); return save(c,f"{OUT}/slide_{idx:02d}.png")

def problem(idx,num,head,sol,frame):
    c=new_canvas((W//2-260,420,W//2+260,1000)); d=ImageDraw.Draw(c)
    draw_logo(c,d)
    badge(c,d,num,W//2,182)
    hf=fit(d,head,BOLD,58,W-MARGIN*2); centered(d,head,250,hf,WHITE)
    sf=fit(d,sol,REG,30,W-MARGIN*2-40,minsz=22); centered(d,sol,322,sf,GREEN)
    place_phone(c,frame,384,sw=296,sh=596)
    footer(c,d); return save(c,f"{OUT}/slide_{idx:02d}.png")

def cta(idx):
    c=new_canvas((W//2-340,160,W//2+340,820)); d=ImageDraw.Draw(c)
    draw_logo(c,d)
    h=180; w=round(LOGO.width*h/LOGO.height)
    c.alpha_composite(LOGO.resize((w,h)),((W-w)//2,210))
    centered(d,"Ditch the spreadsheets.",470,font(BOLD,68),WHITE)
    centered(d,"Run your whole club from one app.",556,font(REG,36),(190,200,218))
    # CTA pill
    cue="Start free  →"; cf=font(BOLD,38); cw=tw(d,cue,cf); pad=44
    px=(W-(cw+pad*2))//2; py=680
    from PIL import Image as I
    pill=I.new("RGBA",(cw+pad*2,86),(0,0,0,0))
    ImageDraw.Draw(pill).rounded_rectangle([0,0,cw+pad*2-1,85],43,fill=GREEN)
    c.alpha_composite(pill,(px,py)); d.text((px+pad,py+22),cue,font=cf,fill=NAVY)
    centered(d,"teamthrive.com",1018,font(REG,30),GREEN)
    return save(c,f"{OUT}/slide_{idx:02d}.png")

i=1
print(cover(i)); i+=1
for num,h,s,fr in ITEMS:
    print(problem(i,num,h,s,fr)); i+=1
print(cta(i))
print("Carousel B done:",i,"slides")
