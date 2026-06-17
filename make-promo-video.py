#!/usr/bin/env python3
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
EX = "/tmp/extract"
FRAMES = "/tmp/frames"
os.makedirs(FRAMES, exist_ok=True)

# Brand palette
GREEN   = (61, 220, 132)
GREEN_D = (30, 140, 84)
NAVY    = (15, 27, 46)
NAVY_D  = (8, 14, 26)
WHITE   = (245, 248, 246)

FB = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
def font(sz): return ImageFont.truetype(FB, sz)

# ---------- helpers ----------
def ease_out(t): return 1 - (1 - t) ** 3
def ease_in_out(t): return 0.5 * (1 - math.cos(math.pi * t)) if 0 <= t <= 1 else (0 if t < 0 else 1)
def clamp01(t): return max(0.0, min(1.0, t))

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def vgrad(top, bot, glow=None):
    """vertical gradient base, optional radial green glow."""
    base = Image.new("RGB", (W, H))
    px = base.load()
    for y in range(H):
        c = lerp(top, bot, y / H)
        for x in range(0, W, 1):
            px[x, y] = c
    if glow:
        gx, gy, gr, gi = glow
        ov = Image.new("RGB", (W, H), (0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=tuple(int(c * gi) for c in GREEN))
        ov = ov.filter(ImageFilter.GaussianBlur(gr // 2))
        base = Image.blend(base, Image.new("RGB", (W, H), (0,0,0)), 0)
        from PIL import ImageChops
        base = ImageChops.add(base, ov)
    return base.convert("RGBA")

def fit_h(img, target_h):
    r = target_h / img.size[1]
    return img.resize((max(1,int(img.size[0]*r)), target_h), Image.LANCZOS)

def fit_w(img, target_w):
    r = target_w / img.size[0]
    return img.resize((target_w, max(1,int(img.size[1]*r))), Image.LANCZOS)

def text_block(draw, lines, cx, cy, fnt, fill, align="center", line_sp=1.12, anchor_v="center", shadow=True):
    sizes = [draw.textbbox((0,0), ln, font=fnt) for ln in lines]
    hs = [(b[3]-b[1]) for b in sizes]
    ws = [(b[2]-b[0]) for b in sizes]
    lh = int(fnt.size * line_sp)
    total = lh * len(lines)
    y = cy - total//2 if anchor_v == "center" else cy
    for i, ln in enumerate(lines):
        w = ws[i]
        if align == "center": x = cx - w//2
        elif align == "left": x = cx
        else: x = cx - w
        ly = y + i*lh - sizes[i][1]
        if shadow:
            draw.text((x+3, ly+4), ln, font=fnt, fill=(0,0,0))
        draw.text((x, ly), ln, font=fnt, fill=fill)
    return total

# Pre-load assets
logo = Image.open("/home/user/team-thrive/teamthrive-logo-shadow.png").convert("RGBA")
crest = Image.open("/home/user/team-thrive/teamthrive-logo.png").convert("RGBA")  # plain
soccer = Image.open(f"{EX}/soccer_cut.png").convert("RGBA")
basket = Image.open(f"{EX}/basket_cut.png").convert("RGBA")
phone  = Image.open(f"{EX}/img_00.png").convert("RGBA")
laptop = Image.open(f"{EX}/img_39.png").convert("RGBA")

# corner logo (persistent brand mark)
corner_w = int(W * 0.13)
corner_logo = fit_w(logo, corner_w)
CMARGIN = int(W * 0.045)

def paste_corner(frame, alpha=1.0):
    if alpha <= 0: return
    cl = corner_logo
    if alpha < 1:
        a = cl.split()[3].point(lambda p: int(p*alpha))
        cl = cl.copy(); cl.putalpha(a)
    frame.alpha_composite(cl, (W - corner_w - CMARGIN, CMARGIN))

def caption_bar(frame, lines, fnt, y_center, pad=34):
    """rounded translucent bar behind caption lines, lower third."""
    d = ImageDraw.Draw(frame)
    maxw = 0
    for ln in lines:
        b = d.textbbox((0,0), ln, font=fnt); maxw = max(maxw, b[2]-b[0])
    lh = int(fnt.size*1.14); th = lh*len(lines)
    bw = maxw + pad*2; bh = th + pad
    bx = W//2 - bw//2; by = y_center - bh//2
    bar = Image.new("RGBA", (bw, bh), (0,0,0,0))
    bd = ImageDraw.Draw(bar)
    bd.rounded_rectangle([0,0,bw,bh], radius=28, fill=(8,14,26,205))
    frame.alpha_composite(bar, (bx, by))
    text_block(d, lines, W//2, y_center, fnt, WHITE, shadow=False)

# ============================================================
# SCENE TIMELINE  (start, dur) in seconds
# ============================================================
def render():
    fi = 0
    def emit(frame):
        nonlocal fi
        frame.convert("RGB").save(f"{FRAMES}/f_{fi:05d}.png")
        fi += 1

    # ---- backgrounds (built once) ----
    bg_navy  = vgrad(NAVY, NAVY_D)
    bg_brand = vgrad((22,40,66), NAVY_D)
    # green glow accent baked
    glow = Image.new("RGBA",(W,H),(0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W*0.1, H*0.55, W*1.1, H*1.4], fill=(GREEN[0],GREEN[1],GREEN[2],70))
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    bg_brand = Image.alpha_composite(bg_brand, glow)
    bg_green = vgrad(GREEN_D, NAVY)
    gglow = Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(gglow).ellipse([W*0.0,-H*0.2,W*1.0,H*0.5], fill=(GREEN[0],GREEN[1],GREEN[2],90))
    bg_green = Image.alpha_composite(bg_green, gglow.filter(ImageFilter.GaussianBlur(160)))

    f_h1 = font(78); f_h2 = font(96); f_sub = font(46); f_cap = font(54)
    f_tag = font(40); f_cta = font(64); f_big = font(120)

    # ---------------- SCENE A: logo reveal (0.0 - 3.2s) ----------------
    nA = int(3.2*FPS)
    big_logo = fit_h(logo, int(H*0.34))
    for i in range(nA):
        t = i/nA
        fr = bg_navy.copy()
        # crest scales/fades in
        s = 0.7 + 0.3*ease_out(clamp01(t/0.55))
        a = ease_out(clamp01(t/0.45))
        lw = max(1,int(big_logo.size[0]*s)); lh = max(1,int(big_logo.size[1]*s))
        ll = big_logo.resize((lw,lh), Image.LANCZOS)
        al = ll.split()[3].point(lambda p:int(p*a)); ll.putalpha(al)
        fr.alpha_composite(ll, (W//2-lw//2, int(H*0.32)-lh//2))
        # tagline fades after 1.1s
        ta = ease_out(clamp01((t-0.35)/0.4))
        if ta>0:
            ov = Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
            text_block(d, ["EVERYTHING YOUR TEAM","NEEDS TO THRIVE"], W//2, int(H*0.60), f_sub,
                       (GREEN[0],GREEN[1],GREEN[2]), shadow=False)
            ovv = Image.new("RGBA",(W,H),(0,0,0,0))
            ovv = Image.blend(ovv, ov, ta)
            fr.alpha_composite(ovv)
        emit(fr)

    # ---------------- SCENE B: hook + soccer (3.2 - 7.6s) ----------------
    nB = int(4.4*FPS)
    sb = fit_h(soccer, int(H*0.72))
    for i in range(nB):
        t = i/nB
        fr = bg_brand.copy()
        # athlete slides from right + settles
        ax = ease_out(clamp01(t/0.5))
        ox = int(W*0.55 + (1-ax)*W*0.5)
        oy = H - sb.size[1] - int(H*0.02)
        sa = ease_out(clamp01(t/0.4))
        sl = sb.copy(); sl.putalpha(sb.split()[3].point(lambda p:int(p*sa)))
        fr.alpha_composite(sl, (ox, oy))
        # headline left, word-by-word
        d = ImageDraw.Draw(fr)
        ha = ease_out(clamp01((t-0.15)/0.5))
        ov = Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
        text_block(od, ["COACHING IS","ABOUT MORE","THAN THE","GAME."], int(W*0.07), int(H*0.34),
                   f_h2, WHITE, align="left", anchor_v="top")
        # green underline accent grows
        uw = int(W*0.30*ha)
        od.rounded_rectangle([int(W*0.07), int(H*0.34)+ int(f_h2.size*1.12*4)+10,
                              int(W*0.07)+uw, int(H*0.34)+int(f_h2.size*1.12*4)+22], radius=6,
                             fill=(GREEN[0],GREEN[1],GREEN[2],255))
        fr.alpha_composite(Image.blend(Image.new("RGBA",(W,H),(0,0,0,0)), ov, ha))
        paste_corner(fr)
        emit(fr)

    # ---------------- SCENE C: app showcase / phone (7.6 - 13.4s) -------
    nC = int(5.8*FPS)
    ph = fit_h(phone, int(H*0.52))
    for i in range(nC):
        t = i/nC
        fr = bg_brand.copy()
        # ken burns zoom on phone mockup
        z = 1.0 + 0.12*ease_in_out(t)
        pw = int(ph.size[0]*z); phh=int(ph.size[1]*z)
        pp = ph.resize((pw,phh), Image.LANCZOS)
        pa = ease_out(clamp01(t/0.3))
        pl = pp.copy(); pl.putalpha(pp.split()[3].point(lambda p:int(p*pa)))
        fr.alpha_composite(pl, (W//2-pw//2, int(H*0.30)-phh//2))
        d=ImageDraw.Draw(fr)
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
        text_block(od, ["ALL YOUR TEAM,","ONE APP"], W//2, int(H*0.12), f_h1, WHITE)
        fr.alpha_composite(Image.blend(Image.new("RGBA",(W,H),(0,0,0,0)),ov,ease_out(clamp01(t/0.3))))
        # caption swaps mid-scene
        if t < 0.5:
            ca = ease_out(clamp01(t/0.18))
            if ca>0: caption_bar(fr, ["Schedules & game-day reminders"], f_cap, int(H*0.78))
        else:
            ca = ease_out(clamp01((t-0.5)/0.18))
            if ca>0: caption_bar(fr, ["Rosters, RSVPs & team chat"], f_cap, int(H*0.78))
        paste_corner(fr)
        emit(fr)

    # ---------------- SCENE D: variety / basketball (13.4 - 17.2s) ------
    nD = int(3.8*FPS)
    bk = fit_h(basket, int(H*0.66))
    for i in range(nD):
        t=i/nD
        fr = bg_brand.copy()
        ax=ease_out(clamp01(t/0.5))
        ox=int(W*0.04 - (1-ax)*W*0.5)
        oy=H-bk.size[1]-int(H*0.04)
        sa=ease_out(clamp01(t/0.4))
        bl=bk.copy(); bl.putalpha(bk.split()[3].point(lambda p:int(p*sa)))
        fr.alpha_composite(bl,(ox,oy))
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
        text_block(od, ["ANY SPORT.","ANY TEAM."], int(W*0.95), int(H*0.30), f_h2, WHITE, align="right", anchor_v="top")
        text_block(od, ["Soccer, basketball &","every season between"], int(W*0.95), int(H*0.52), f_tag, (GREEN[0],GREEN[1],GREEN[2]), align="right", anchor_v="top", shadow=False)
        fr.alpha_composite(Image.blend(Image.new("RGBA",(W,H),(0,0,0,0)),ov,ease_out(clamp01((t-0.1)/0.4))))
        paste_corner(fr)
        emit(fr)

    # ---------------- SCENE E: value props (17.2 - 22.0s) ---------------
    nE = int(4.8*FPS)
    props = ["Smart scheduling", "Instant parent updates", "Everyone on the same page"]
    for i in range(nE):
        t=i/nE
        fr = bg_navy.copy()
        d=ImageDraw.Draw(fr)
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
        text_block(od, ["BUILT FOR BUSY","COACHES"], W//2, int(H*0.16), f_h1, WHITE)
        fr.alpha_composite(Image.blend(Image.new("RGBA",(W,H),(0,0,0,0)),ov,ease_out(clamp01(t/0.25))))
        # checklist items stagger in
        y0 = int(H*0.42); rowh=int(H*0.12)
        for k, p in enumerate(props):
            ta = ease_out(clamp01((t-(0.2+0.18*k))/0.3))
            if ta<=0: continue
            row = Image.new("RGBA",(W,H),(0,0,0,0)); rd=ImageDraw.Draw(row)
            cx0 = int(W*0.12); cy0 = y0+rowh*k
            # check circle
            rd.ellipse([cx0, cy0, cx0+70, cy0+70], fill=(GREEN[0],GREEN[1],GREEN[2],255))
            rd.line([cx0+18,cy0+36, cx0+30,cy0+50], fill=(8,14,26), width=9)
            rd.line([cx0+30,cy0+50, cx0+54,cy0+20], fill=(8,14,26), width=9)
            rd.text((cx0+100, cy0+4), p, font=f_sub, fill=WHITE)
            dx = int((1-ta)*60)
            fr.alpha_composite(Image.blend(Image.new("RGBA",(W,H),(0,0,0,0)),row,ta), (dx,0))
        paste_corner(fr)
        emit(fr)

    # ---------------- SCENE F: payoff + CTA (22.0 - 27.5s) --------------
    nF = int(5.5*FPS)
    big = fit_h(logo, int(H*0.26))
    for i in range(nF):
        t=i/nF
        fr = bg_green.copy()
        s=0.85+0.15*ease_out(clamp01(t/0.4)); a=ease_out(clamp01(t/0.35))
        lw=int(big.size[0]*s); lh=int(big.size[1]*s)
        ll=big.resize((lw,lh),Image.LANCZOS); ll.putalpha(ll.split()[3].point(lambda p:int(p*a)))
        fr.alpha_composite(ll,(W//2-lw//2,int(H*0.26)-lh//2))
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
        text_block(od, ["EVERYTHING YOUR TEAM","NEEDS TO THRIVE"], W//2, int(H*0.50), f_sub, WHITE)
        fr.alpha_composite(Image.blend(Image.new("RGBA",(W,H),(0,0,0,0)),ov,ease_out(clamp01((t-0.2)/0.3))))
        # CTA pill
        ca=ease_out(clamp01((t-0.45)/0.3))
        if ca>0:
            pill=Image.new("RGBA",(W,H),(0,0,0,0)); pd=ImageDraw.Draw(pill)
            bw=int(W*0.66); bh=130; bx=W//2-bw//2; by=int(H*0.62)
            pd.rounded_rectangle([bx,by,bx+bw,by+bh],radius=65,fill=WHITE)
            b=pd.textbbox((0,0),"Download Team Thrive",font=f_cta)
            pd.text((W//2-(b[2]-b[0])//2, by+bh//2-(b[3]-b[1])//2-b[1]), "Download Team Thrive", font=f_cta, fill=NAVY)
            sc=0.9+0.1*ca
            fr.alpha_composite(Image.blend(Image.new("RGBA",(W,H),(0,0,0,0)),pill,ca))
        emit(fr)

    return fi

total = render()
print("FRAMES", total)
