#!/usr/bin/env python3
"""Reel 1 — Team Thrive app demo: intro, hook, swipe through screens, CTA."""
import numpy as np, imageio, os
from PIL import Image, ImageDraw
from video_engine import *

OUT="instagram-reels"; os.makedirs(OUT,exist_ok=True)
DUR=16.2
TY=760  # phone top in features

FEATURES=[("Team Chat",134),("Schedule & Events",25),("Payments",122),
          ("Roster",28),("Athlete Profiles",92)]
SCR=[(lbl,prep_screen(fr)) for lbl,fr in FEATURES]

FB,FE=4.6,13.4
def features_state(t):
    dur=FE-FB; per=dur/len(SCR); local=t-FB
    idx=max(0,min(len(SCR)-1,int(local/per))); within=local-idx*per
    trans=0.42; prog=0.0; nxt=idx
    if within>per-trans and idx<len(SCR)-1:
        prog=ease_io((within-(per-trans))/trans); nxt=idx+1
    return idx,nxt,prog,within,per

def render(t):
    f=BG_MID.convert("RGBA")

    # ---- INTRO 0-2.2 : logo scales in + wordmark + tagline ----
    if t<2.4:
        a=ease_out(seg(t,0.1,0.9)); s=lerp(0.7,1.0,ease_back(clamp01(seg(t,0.1,1.0))))
        draw_logo_mark(f,W//2,760,int(300*s),alpha=a)
        wf=text_layer("TEAM THRIVE",font(BOLD,86),WHITE)
        paste_alpha(f,wf,(center_x(wf),960),alpha=ease_out(seg(t,0.6,1.3)))
        tg=text_layer("Youth sports management, simplified.",font(REG,40),SUB)
        paste_alpha(f,tg,(center_x(tg),1075),alpha=ease_out(seg(t,1.0,1.7)))

    # ---- HOOK 2.2-4.6 : kinetic text ----
    if 2.2<=t<4.8:
        a1=ease_out(seg(t,2.3,2.9)); y1=lerp(880,840,a1)
        l1=text_layer("Running your club",font(BOLD,84),WHITE)
        paste_alpha(f,l1,(center_x(l1),int(y1)),alpha=a1)
        a2=ease_out(seg(t,2.8,3.4)); y2=lerp(1000,960,a2)
        l2=text_layer("shouldn't be chaos.",font(BOLD,84),GREEN)
        paste_alpha(f,l2,(center_x(l2),int(y2)),alpha=a2)
        a3=ease_out(seg(t,3.7,4.3))
        l3=text_layer("There's one app for all of it  →",font(REG,42),SUB)
        paste_alpha(f,l3,(center_x(l3),1110),alpha=a3*(1-seg(t,4.5,4.8)))

    # ---- FEATURES 4.2-13.4 : phone rises, swipe screens ----
    if 4.2<=t<13.9:
        py=lerp(1920,TY,ease_out(seg(t,4.2,4.9)))
        if t>=13.4: py=lerp(TY,1920,ease_io(seg(t,13.4,13.9)))
        pa=seg(t,4.2,4.7)*(1-seg(t,13.5,13.9))
        idx,nxt,prog,within,per=features_state(min(t,FE-0.01))
        scrA=SCR[idx][1]; scrB=SCR[nxt][1]
        layer=screen_swipe(scrA,scrB,prog) if prog>0 else (lambda l:(l.paste(scrA,(0,0)) or l))(Image.new("RGBA",(SW,SH),(0,0,0,0)))
        phone=phone_with_screen(layer)
        px=(W-PW)//2
        sh=shadow_for(px,int(py),PW,PH);
        if pa<1.0:
            aa=sh.split()[3].point(lambda p:int(p*pa)); sh.putalpha(aa)
        f.alpha_composite(sh)
        paste_alpha(f,phone,(px,int(py)),alpha=pa)
        # label chip above
        lbl=SCR[idx][0]
        la=ease_back(clamp01(seg(within,0.0,0.35)))*pa
        ltxt=text_layer(lbl,font(BOLD,64),WHITE)
        paste_alpha(f,ltxt,(center_x(ltxt),600),alpha=clamp01(la),scale=lerp(0.9,1.0,clamp01(la)))
        # progress dots
        for k in range(len(SCR)):
            cx=W//2-(len(SCR)-1)*22//2+k*22
            col=GREEN if k==idx else (90,105,140)
            ImageDraw.Draw(f).ellipse([cx-6,690-6,cx+6,690+6],fill=col)
        logo_lockup_topleft(f,alpha=pa)

    # ---- CTA 13.5-16.2 ----
    if t>=13.5:
        a=ease_out(seg(t,13.7,14.4))
        draw_logo_mark(f,W//2,640,int(220*lerp(0.85,1.0,a)),alpha=a)
        l1=text_layer("Everything your club needs.",font(BOLD,66),WHITE)
        paste_alpha(f,l1,(center_x(l1),820),alpha=ease_out(seg(t,14.0,14.6)))
        l2=text_layer("One app.",font(BOLD,84),GREEN)
        paste_alpha(f,l2,(center_x(l2),910),alpha=ease_out(seg(t,14.3,14.9)))
        # pill
        pa=ease_out(seg(t,14.7,15.3))
        if pa>0:
            cue="teamthrive.com"; cf=font(BOLD,46); tl=text_layer(cue,cf,NAVY)
            pw=tl.width+96; ph2=104; px=(W-pw)//2; py=1080
            pill=Image.new("RGBA",(pw,ph2),(0,0,0,0))
            ImageDraw.Draw(pill).rounded_rectangle([0,0,pw-1,ph2-1],ph2//2,fill=GREEN)
            pill.alpha_composite(tl,((pw-tl.width)//2,(ph2-tl.height)//2))
            paste_alpha(f,pill,(px,py),alpha=pa)

    return np.asarray(f.convert("RGB"))

def main():
    out=f"{OUT}/reel-app-demo.mp4"
    w=imageio.get_writer(out,fps=FPS,codec="libx264",quality=8,
                         macro_block_size=1,ffmpeg_params=["-pix_fmt","yuv420p"])
    n=int(DUR*FPS)
    for i in range(n):
        w.append_data(render(i/FPS))
    w.close()
    print("wrote",out,n,"frames",round(DUR,1),"s")

if __name__=="__main__": main()
