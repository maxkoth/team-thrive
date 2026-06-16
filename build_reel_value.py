#!/usr/bin/env python3
"""Reel 2 — fast kinetic value montage: flashing words, zooming screens, CTA."""
import numpy as np, imageio, os
from PIL import Image, ImageDraw
from video_engine import *

OUT="instagram-reels"; os.makedirs(OUT,exist_ok=True)
DUR=15.6; TY=720

WORDS=["Chats.","Schedules.","Payments.","Rosters.","Profiles."]
FEATURES=[("Team chat",134),("Live schedule",25),("Easy payments",122),
          ("Full roster",28),("Parent portal",93),("Club dashboard",44)]
SCR=[(lbl,prep_screen(fr)) for lbl,fr in FEATURES]

def screen_zoom(scr,scale):
    nw,nh=int(SW*scale),int(SH*scale)
    z=scr.resize((nw,nh),Image.LANCZOS)
    x=(nw-SW)//2; y=(nh-SH)//2
    return z.crop((x,y,x+SW,y+SH)).convert("RGBA")

FB,FE=3.2,12.6
def feat_state(t):
    dur=FE-FB; per=dur/len(SCR); local=t-FB
    idx=max(0,min(len(SCR)-1,int(local/per))); within=local-idx*per
    return idx,within,per

def render(t):
    f=BG_MID.convert("RGBA")
    logo_lockup_topleft(f,alpha=clamp01(seg(t,0.1,0.6)))

    # ---- 0.2-2.0 flashing words ----
    if t<2.1:
        per=0.34; i=int((t-0.15)/per)
        if 0<=i<len(WORDS):
            w0=0.15+i*per; lp=seg(t,w0,w0+0.12); fade=1-seg(t,w0+per-0.08,w0+per)
            col=GREEN if i%2 else WHITE
            wl=text_layer(WORDS[i],font(BOLD,108),col)
            paste_alpha(f,wl,(center_x(wl),870),alpha=clamp01(lp*fade),
                        scale=lerp(0.8,1.0,ease_back(clamp01(lp))))

    # ---- 2.0-3.2 "All in one app." ----
    if 2.0<=t<3.4:
        a=ease_back(clamp01(seg(t,2.05,2.6)))
        l1=text_layer("All in",font(BOLD,96),WHITE)
        paste_alpha(f,l1,(center_x(l1),820),alpha=clamp01(seg(t,2.05,2.5)),scale=lerp(0.8,1,a))
        l2=text_layer("one app.",font(BOLD,116),GREEN)
        paste_alpha(f,l2,(center_x(l2),940),alpha=clamp01(seg(t,2.25,2.7)),scale=lerp(0.8,1,a))

    # ---- 3.0-12.6 screen montage (crossfade + zoom) ----
    if 3.0<=t<13.1:
        pa=seg(t,3.0,3.5)*(1-seg(t,12.7,13.1))
        idx,within,per=feat_state(min(t,FE-0.01))
        zoom=lerp(1.10,1.0,ease_out(clamp01(within/per)))   # slow zoom-out each hold
        layer=screen_zoom(SCR[idx][1],zoom)
        if within<0.32 and idx>0:                            # crossfade from prev
            prev=screen_zoom(SCR[idx-1][1],1.0)
            base=prev.copy(); fade=ease_io(within/0.32)
            a=layer.split()[3].point(lambda p:int(p*fade)); layer.putalpha(a)
            base.alpha_composite(layer); layer=base
        phone=phone_with_screen(layer)
        px=(W-PW)//2; py=TY
        sh=shadow_for(px,py,PW,PH)
        if pa<1.0: sh.putalpha(sh.split()[3].point(lambda p:int(p*pa)))
        f.alpha_composite(sh); paste_alpha(f,phone,(px,py),alpha=pa)
        # big label that slides up
        lbl=SCR[idx][0]; la=ease_out(clamp01(seg(within,0.0,0.3)))*pa
        ly=lerp(620,600,la)
        lt=text_layer(lbl,font(BOLD,72),WHITE)
        paste_alpha(f,lt,(center_x(lt),int(ly)),alpha=clamp01(la))
        # accent underline
        if la>0.3:
            uw=int(lt.width*0.5); ux=W//2-uw//2
            ImageDraw.Draw(f).rounded_rectangle([ux,690,ux+uw,698],4,fill=GREEN)

    # ---- CTA 12.7-15.6 ----
    if t>=12.7:
        a=ease_out(seg(t,12.9,13.6))
        draw_logo_mark(f,W//2,650,int(230*lerp(0.85,1,a)),alpha=a)
        l1=text_layer("Your whole club,",font(BOLD,72),WHITE)
        paste_alpha(f,l1,(center_x(l1),840),alpha=ease_out(seg(t,13.2,13.8)))
        l2=text_layer("one simple app.",font(BOLD,72),GREEN)
        paste_alpha(f,l2,(center_x(l2),930),alpha=ease_out(seg(t,13.45,14.05)))
        pa=ease_out(seg(t,13.9,14.5))
        if pa>0:
            cue="teamthrive.com"; cf=font(BOLD,46); tl=text_layer(cue,cf,NAVY)
            pw=tl.width+96; ph2=104; px=(W-pw)//2; py=1090
            pill=Image.new("RGBA",(pw,ph2),(0,0,0,0))
            ImageDraw.Draw(pill).rounded_rectangle([0,0,pw-1,ph2-1],ph2//2,fill=GREEN)
            pill.alpha_composite(tl,((pw-tl.width)//2,(ph2-tl.height)//2))
            paste_alpha(f,pill,(px,py),alpha=pa)
    return np.asarray(f.convert("RGB"))

def main():
    out=f"{OUT}/reel-value-montage.mp4"
    w=imageio.get_writer(out,fps=FPS,codec="libx264",quality=8,
                         macro_block_size=1,ffmpeg_params=["-pix_fmt","yuv420p"])
    for i in range(int(DUR*FPS)): w.append_data(render(i/FPS))
    w.close(); print("wrote",out,int(DUR*FPS),"frames")

if __name__=="__main__": main()
