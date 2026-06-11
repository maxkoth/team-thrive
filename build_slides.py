#!/usr/bin/env python3
"""Build Team Thrive Instagram carousel slides (1080x1080) from extracted app screens."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NAVY = (13, 27, 62)        # #0D1B3E
GREEN = (61, 220, 132)     # #3DDC84
WHITE = (255, 255, 255)
SCREEN_BG = (5, 8, 15)     # phone body / near-black

FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
BOLD = os.path.join(FONT_DIR, "Outfit-Bold.ttf")
REG = os.path.join(FONT_DIR, "Outfit-Regular.ttf")

SRC = "figma-assets/screens"
OUT = "instagram-carousel"
os.makedirs(OUT, exist_ok=True)

# (frame number, headline, one-line description)
SLIDES = [
    (134, "Centralized Communication", "Team chats, announcements & updates in one place"),
    (28,  "Roster Management",          "Add and manage players, coaches & staff in seconds"),
    (25,  "Scheduling & Events",        "Games, practices & RSVPs — always in sync"),
    (122, "Payments & Invoicing",       "Collect dues and send invoices effortlessly"),
    (92,  "Athlete Profiles",           "Every athlete’s info, stats & progress at a glance"),
    (93,  "Parent Portal",              "Connect parents to their athletes and keep them looped in"),
    (27,  "Team Dashboard",             "Your whole team’s activity in a single view"),
    (105, "Coach Tools",                "Everything coaches need to lead with confidence"),
    (44,  "Club Management",            "Run every team in your club from one app"),
]

W = H = 1080
MARGIN = 80

def font(path, size):
    return ImageFont.truetype(path, size)

def text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]

def fit_font(d, s, path, start, maxw, minsz=40):
    sz = start
    while sz > minsz and text_w(d, s, font(path, sz)) > maxw:
        sz -= 2
    return font(path, sz)

def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0]-1, size[1]-1], radius, fill=255)
    return m

def phone_mockup(screen_img, screen_w, screen_h):
    """Return an RGBA phone mockup image (bezel + screen) sized to screen + bezel."""
    bezel = 14
    radius_out = 54
    radius_in = 40
    pw, ph = screen_w + bezel*2, screen_h + bezel*2
    phone = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    # body
    body = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle([0, 0, pw-1, ph-1], radius_out, fill=SCREEN_BG+(255,))
    phone.alpha_composite(body)
    # subtle hairline border
    ImageDraw.Draw(phone).rounded_rectangle([0, 0, pw-1, ph-1], radius_out,
                                            outline=(70, 90, 130, 180), width=2)
    # screen (rounded)
    scr = screen_img.convert("RGBA").resize((screen_w, screen_h))
    scr.putalpha(rounded_mask((screen_w, screen_h), radius_in))
    phone.alpha_composite(scr, (bezel, bezel))
    return phone

def prep_screen(frame, target_w, target_h):
    im = Image.open(f"{SRC}/frame_{frame:03d}.png").convert("RGB")
    scale = target_w / im.width
    im = im.resize((target_w, round(im.height * scale)))
    # crop top portion to phone aspect (handles tall scroll views)
    return im.crop((0, 0, target_w, min(im.height, target_h)))

LOGO = Image.open("figma-assets/logo_teamthrive_mark.png").convert("RGBA")

def draw_logo(canvas, d):
    """Real Team Thrive shield mark + 'Team Thrive' wordmark, top-left lockup."""
    x, y = MARGIN, 52
    h = 66
    w = round(LOGO.width * h / LOGO.height)
    mark = LOGO.resize((w, h))
    canvas.alpha_composite(mark, (x, y))
    wf = font(BOLD, 36)
    d.text((x + w + 20, y + (h - 36)//2 - 2), "Team Thrive", font=wf, fill=WHITE)

def build(frame, headline, desc, idx):
    canvas = Image.new("RGBA", (W, H), NAVY + (255,))
    d = ImageDraw.Draw(canvas)

    # soft green glow behind phone for depth
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W//2-280, 430, W//2+280, 1010], fill=GREEN+(46,))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))

    draw_logo(canvas, d)

    # headline (centered, auto-fit)
    hf = fit_font(d, headline, BOLD, 60, W - MARGIN*2)
    hb = d.textbbox((0, 0), headline, font=hf)
    d.text(((W - (hb[2]-hb[0]))//2, 170), headline, font=hf, fill=WHITE)

    # description (centered, green)
    df = fit_font(d, desc, REG, 30, W - MARGIN*2 - 40, minsz=22)
    db = d.textbbox((0, 0), desc, font=df)
    d.text(((W - (db[2]-db[0]))//2, 246), desc, font=df, fill=GREEN)

    # phone mockup
    screen_w, screen_h = 300, 650
    scr = prep_screen(frame, screen_w, screen_h)
    phone = phone_mockup(scr, screen_w, screen_h)
    pw, ph = phone.size
    px, py = (W - pw)//2, 312

    # drop shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([px, py+18, px+pw, py+ph+18], 54, fill=(0, 0, 0, 150))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(28)))
    canvas.alpha_composite(phone, (px, py))

    # footer url
    ff = font(REG, 26)
    fb = d.textbbox((0, 0), "teamthrive.com", font=ff)
    d.text(((W - (fb[2]-fb[0]))//2, 1018), "teamthrive.com", font=ff, fill=GREEN)

    out = f"{OUT}/slide_{idx:02d}.png"
    canvas.convert("RGB").save(out, "PNG")
    return out

def build_cover(idx):
    canvas = Image.new("RGBA", (W, H), NAVY + (255,))
    d = ImageDraw.Draw(canvas)

    # green glow (centered, larger)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W//2-340, 120, W//2+340, 760], fill=GREEN+(46,))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(110)))

    # big centered shield logo
    lh = 188
    lw = round(LOGO.width * lh / LOGO.height)
    canvas.alpha_composite(LOGO.resize((lw, lh)), ((W - lw)//2, 150))
    # wordmark
    wf = font(BOLD, 50)
    wb = d.textbbox((0, 0), "TEAM THRIVE", font=wf)
    d.text(((W - (wb[2]-wb[0]))//2, 150 + lh + 18), "TEAM THRIVE", font=wf, fill=WHITE)

    # hook headline (two lines, centered)
    lines = ["Everything your club", "needs in one app"]
    hf = font(BOLD, 82)
    y = 560
    for ln in lines:
        b = d.textbbox((0, 0), ln, font=hf)
        d.text(((W - (b[2]-b[0]))//2, y), ln, font=hf, fill=WHITE)
        y += 92

    # subtitle (green)
    sub = "Youth sports management, simplified."
    sf = font(REG, 36)
    sb = d.textbbox((0, 0), sub, font=sf)
    d.text(((W - (sb[2]-sb[0]))//2, y + 20), sub, font=sf, fill=GREEN)

    # "Swipe" pill cue
    cue = "Swipe to explore  →"
    cf = font(BOLD, 34)
    cb = d.textbbox((0, 0), cue, font=cf)
    cw = cb[2]-cb[0]
    pad = 36
    px0 = (W - (cw + pad*2))//2
    py0 = 880
    pill = Image.new("RGBA", (cw + pad*2, 76), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([0, 0, cw + pad*2 - 1, 75], 38, fill=GREEN)
    canvas.alpha_composite(pill, (px0, py0))
    d.text((px0 + pad, py0 + 38 - (cb[3]-cb[1])//2 - cb[1]), cue, font=cf, fill=NAVY)

    # footer url
    ff = font(REG, 26)
    fb = d.textbbox((0, 0), "teamthrive.com", font=ff)
    d.text(((W - (fb[2]-fb[0]))//2, 1018), "teamthrive.com", font=ff, fill=GREEN)

    out = f"{OUT}/slide_{idx:02d}.png"
    canvas.convert("RGB").save(out, "PNG")
    return out

print("built", build_cover(1))                       # cover = slide_01
for i, (frame, head, desc) in enumerate(SLIDES, 2):   # features = slide_02..10
    print("built", build(frame, head, desc, i))
print("done")
