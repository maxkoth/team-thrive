#!/usr/bin/env python3
"""Carousel C — 'One app. Every role.' persona-based slides with label chips."""
import os
from PIL import ImageDraw, Image
from slide_common import (W,H,MARGIN,NAVY,GREEN,WHITE,BOLD,REG,font,fit,centered,tw,
                          new_canvas,draw_logo,footer,place_phone,save,LOGO)

OUT="carousel-c"; os.makedirs(OUT,exist_ok=True)

# (chip label, headline, green benefit, frame)
ITEMS=[
    ("FOR COACHES","Lead your team with ease","Rosters, schedules & team comms in one place.",28),
    ("FOR PARENTS","Never miss a beat","Schedules, payments & messages at your fingertips.",93),
    ("FOR CLUB ADMINS","Run the whole club","Manage every team & track payments club-wide.",44),
    ("FOR ATHLETES","Everything in your pocket","Your team, schedule & profile in one app.",92),
]

def chip(canvas,d,label,cy=158):
    f=font(BOLD,28); w=tw(d,label,f); pad=28; h=52
    x0=(W-(w+pad*2))//2
    pill=Image.new("RGBA",(w+pad*2,h),(0,0,0,0))
    ImageDraw.Draw(pill).rounded_rectangle([0,0,w+pad*2-1,h-1],h//2,fill=GREEN)
    canvas.alpha_composite(pill,(x0,cy))
    d.text((x0+pad,cy+13),label,font=f,fill=NAVY)

def cover(idx):
    c=new_canvas((W//2-340,120,W//2+340,720)); d=ImageDraw.Draw(c)
    draw_logo(c,d)
    centered(d,"One app.",330,font(BOLD,96),WHITE)
    centered(d,"Every role.",438,font(BOLD,96),GREEN)
    centered(d,"Built for everyone in your club.",600,font(REG,38),(190,200,218))
    cue="Swipe  →"; cf=font(BOLD,34); cw=tw(d,cue,cf); pad=36
    px=(W-(cw+pad*2))//2; py=760
    pill=Image.new("RGBA",(cw+pad*2,76),(0,0,0,0))
    ImageDraw.Draw(pill).rounded_rectangle([0,0,cw+pad*2-1,75],38,fill=GREEN)
    c.alpha_composite(pill,(px,py)); d.text((px+pad,py+20),cue,font=cf,fill=NAVY)
    footer(c,d); return save(c,f"{OUT}/slide_{idx:02d}.png")

def persona(idx,label,head,benefit,frame):
    c=new_canvas((W//2-260,420,W//2+260,1000)); d=ImageDraw.Draw(c)
    draw_logo(c,d)
    chip(c,d,label)
    hf=fit(d,head,BOLD,60,W-MARGIN*2); centered(d,head,236,hf,WHITE)
    bf=fit(d,benefit,REG,30,W-MARGIN*2-40,minsz=22); centered(d,benefit,310,bf,GREEN)
    place_phone(c,frame,378,sw=296,sh=600)
    footer(c,d); return save(c,f"{OUT}/slide_{idx:02d}.png")

def cta(idx):
    c=new_canvas((W//2-340,160,W//2+340,820)); d=ImageDraw.Draw(c)
    draw_logo(c,d)
    h=180; w=round(LOGO.width*h/LOGO.height)
    c.alpha_composite(LOGO.resize((w,h)),((W-w)//2,210))
    centered(d,"Whatever your role,",470,font(BOLD,66),WHITE)
    centered(d,"Team Thrive fits.",548,font(BOLD,66),GREEN)
    cue="Get started  →"; cf=font(BOLD,38); cw=tw(d,cue,cf); pad=44
    px=(W-(cw+pad*2))//2; py=700
    pill=Image.new("RGBA",(cw+pad*2,86),(0,0,0,0))
    ImageDraw.Draw(pill).rounded_rectangle([0,0,cw+pad*2-1,85],43,fill=GREEN)
    c.alpha_composite(pill,(px,py)); d.text((px+pad,py+22),cue,font=cf,fill=NAVY)
    centered(d,"teamthrive.com",1018,font(REG,30),GREEN)
    return save(c,f"{OUT}/slide_{idx:02d}.png")

i=1
print(cover(i)); i+=1
for label,h,b,fr in ITEMS:
    print(persona(i,label,h,b,fr)); i+=1
print(cta(i))
print("Carousel C done:",i,"slides")
