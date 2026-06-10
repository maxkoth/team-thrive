#!/usr/bin/env python3
"""Build Team Thrive Instagram carousel slides (1080x1080) from app screenshots.

Each slide: navy background, phone mockup of the screenshot centered, a bold white
headline at top, a green one-line description, the Team Thrive logo/wordmark in the
top-left, and "teamthrive.com" centered at the bottom.
"""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "assets", "fonts")
SCREENS = os.path.join(ROOT, "work", "screens")
OUT = os.path.join(ROOT, "slides")
os.makedirs(OUT, exist_ok=True)

# Brand
NAVY = (13, 27, 62)        # #0D1B3E
GREEN = (61, 220, 132)     # #3DDC84
WHITE = (255, 255, 255)
SCREEN_BG = (8, 16, 38)    # slightly darker navy for letterboxing inside phone

SS = 2  # supersample factor for crisp output
W = H = 1080 * SS

def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f"BarlowCondensed-{weight}.ttf"), size * SS)

def text_w(draw, s, f):
    b = draw.textbbox((0, 0), s, font=f)
    return b[2] - b[0]

def fit_font(draw, s, weight, start, maxw, minsize=20):
    size = start
    while size > minsize:
        f = font(weight, size)
        if text_w(draw, s, f) <= maxw * SS:
            return f
        size -= 1
    return font(weight, minsize)

def wrap(draw, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(draw, t, f) <= maxw * SS:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def rounded(size, radius, fill):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill)
    return img

def phone_mockup(shot, target_h):
    """Render a phone-frame mockup containing `shot`, scaled so total height ~= target_h."""
    sw, sh = shot.size
    # Screen aspect from the screenshot; clamp to a sensible phone range.
    aspect = sw / sh
    aspect = max(0.42, min(aspect, 0.62))  # width/height of the screen area
    bezel = int(16 * SS)
    radius = int(46 * SS)
    inner_radius = int(34 * SS)

    screen_h = target_h - 2 * bezel
    screen_w = int(screen_h * aspect)
    body_w = screen_w + 2 * bezel
    body_h = screen_h + 2 * bezel

    # Body
    body = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.rounded_rectangle([0, 0, body_w - 1, body_h - 1], radius=radius, fill=(6, 11, 26, 255))
    # thin green-tinted rim
    bd.rounded_rectangle([0, 0, body_w - 1, body_h - 1], radius=radius,
                         outline=(61, 220, 132, 90), width=max(1, int(1.5 * SS)))

    # Screen content: fit screenshot (contain) onto screen background
    screen = Image.new("RGBA", (screen_w, screen_h), SCREEN_BG + (255,))
    scale = min(screen_w / sw, screen_h / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    shot_r = shot.resize((nw, nh), Image.LANCZOS)
    screen.paste(shot_r, ((screen_w - nw) // 2, (screen_h - nh) // 2), shot_r if shot_r.mode == "RGBA" else None)
    # round the screen corners
    mask = Image.new("L", (screen_w, screen_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, screen_w - 1, screen_h - 1], radius=inner_radius, fill=255)
    body.paste(screen, (bezel, bezel), mask)

    # Dynamic-island pill
    pill_w, pill_h = int(screen_w * 0.34), int(11 * SS)
    pd = ImageDraw.Draw(body)
    px = (body_w - pill_w) // 2
    py = bezel + int(10 * SS)
    pd.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=pill_h // 2, fill=(0, 0, 0, 255))

    return body

def build(shot_path, headline, desc, out_name):
    canvas = Image.new("RGBA", (W, H), NAVY + (255,))
    draw = ImageDraw.Draw(canvas)

    margin = 70 * SS

    # --- Top-left branding: shield + wordmark ---
    shield = Image.open(os.path.join(ROOT, "assets", "shield_t.png")).convert("RGBA")
    sh_h = 78 * SS
    sh_w = int(shield.width * sh_h / shield.height)
    shield = shield.resize((sh_w, sh_h), Image.LANCZOS)
    brand_y = 56 * SS
    canvas.paste(shield, (margin, brand_y), shield)
    wf = font("800", 30)
    wm = "TEAM THRIVE"
    draw.text((margin + sh_w + 18 * SS, brand_y + sh_h // 2), wm,
              font=wf, fill=GREEN, anchor="lm")

    # --- Headline (white, bold, large, centered) ---
    hf = fit_font(draw, headline, "800", 76, 1080 - 160)
    hy = 168 * SS
    draw.text((W // 2, hy), headline, font=hf, fill=WHITE, anchor="mm")
    hb = draw.textbbox((W // 2, hy), headline, font=hf, anchor="mm")

    # --- Description (green, one line, centered) ---
    df = fit_font(draw, desc, "600", 36, 1080 - 150, minsize=24)
    dy = hb[3] + 30 * SS
    draw.text((W // 2, dy), desc, font=df, fill=GREEN, anchor="mm")
    db = draw.textbbox((W // 2, dy), desc, font=df, anchor="mm")

    # --- Footer: teamthrive.com ---
    ff = font("600", 26)
    fy = H - 58 * SS
    draw.text((W // 2, fy), "teamthrive.com", font=ff, fill=GREEN, anchor="mm")
    fb = draw.textbbox((W // 2, fy), "teamthrive.com", font=ff, anchor="mm")

    # --- Phone mockup centered in remaining space ---
    top = db[3] + 34 * SS
    bottom = fb[1] - 30 * SS
    avail_h = bottom - top
    target_h = min(avail_h, int(720 * SS))

    shot = Image.open(shot_path).convert("RGBA")
    phone = phone_mockup(shot, target_h)
    # if too wide, rescale to fit width
    maxw = int(560 * SS)
    if phone.width > maxw:
        r = maxw / phone.width
        phone = phone.resize((int(phone.width * r), int(phone.height * r)), Image.LANCZOS)

    px = (W - phone.width) // 2
    py = top + (avail_h - phone.height) // 2

    # soft drop shadow
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([px, py + 14 * SS, px + phone.width, py + phone.height + 14 * SS],
                         radius=46 * SS, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(26 * SS))
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.paste(phone, (px, py), phone)

    final = canvas.convert("RGB").resize((1080, 1080), Image.LANCZOS)
    out_path = os.path.join(OUT, out_name)
    final.save(out_path, "PNG")
    print("wrote", out_path)

def main():
    manifest = json.load(open(os.path.join(ROOT, "slides_manifest.json")))
    for item in manifest:
        sp = os.path.join(SCREENS, item["screen"])
        build(sp, item["headline"], item["desc"], item["out"])

if __name__ == "__main__":
    main()
