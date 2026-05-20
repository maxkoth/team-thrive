#!/usr/bin/env python3
"""
fix_slides_v2.py

1. Rebuild Product Roadmap (id_22682c1b6c814be1) for 13.33" widescreen slide
2. Rebuild Our Team       (id_28e03f1590b44fbb) for 13.33" widescreen slide
3. Replace 14 broken image elements on slides 16, 19, 29, 30, 31
   with styled emoji placeholders

Root insight: slide canvas is 13.3333" × 7.5" (12,192,000 × 6,858,000 EMU),
not the 10" width used in fix_new_slides.py.
"""

import os, sys, uuid, httplib2, google_auth_httplib2
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as SA

PRESENTATION_ID  = '1FNIUCC8jPqpwL8xTrQ33J3vGFwuaULhyp_BknKOuIjk'
SCOPES           = ['https://www.googleapis.com/auth/presentations']
ROADMAP_ID       = 'id_22682c1b6c814be1'
TEAM_ID          = 'id_28e03f1590b44fbb'

# ── Colours ───────────────────────────────────────────────────────────────────

def rgb(h):
    h = h.lstrip('#')
    return {'red': int(h[0:2],16)/255, 'green': int(h[2:4],16)/255, 'blue': int(h[4:6],16)/255}

NAVY     = rgb('0D1B3E')
GREEN    = rgb('3DDC84')
WHITE    = {'red':1.0,'green':1.0,'blue':1.0}
GRAY     = rgb('8892A4')
DKNAVY   = rgb('08122A')
MDNAVY   = rgb('0F2347')
BLUGRAY  = rgb('B0BCCC')
BORD     = rgb('1C3060')
DARKCARD = rgb('0A1428')
DKGREEN  = rgb('0D1B3E')  # text on green bg

# ── Units ─────────────────────────────────────────────────────────────────────

def emu(inches): return int(inches * 914_400)
def pt(p):       return int(p * 12_700)
def _v(v):       return {'magnitude': v, 'unit': 'EMU'}

BASE =  3_000_000       # Google Slides shape base size (EMU)
W    = 12_192_000       # 13.3333" slide width
H    =  6_858_000       # 7.5"  slide height

# ── Auth ─────────────────────────────────────────────────────────────────────

def get_service():
    ca  = os.environ.get('REQUESTS_CA_BUNDLE', '/etc/ssl/certs/ca-certificates.crt')
    key = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')
    if not os.path.exists(key):
        sys.exit(f'Key not found: {key}')
    creds = SA.from_service_account_file(key, scopes=SCOPES)
    h = httplib2.Http(ca_certs=ca)
    return build('slides', 'v1', http=google_auth_httplib2.AuthorizedHttp(creds, http=h))

def get_pres(svc):
    return svc.presentations().get(presentationId=PRESENTATION_ID).execute()

def batch(svc, reqs):
    if not reqs:
        return
    return svc.presentations().batchUpdate(
        presentationId=PRESENTATION_ID, body={'requests': reqs}
    ).execute()

def _oid():
    return 'v2_' + uuid.uuid4().hex[:16]

# ── Shape factory (scaleX/scaleY sizing) ─────────────────────────────────────
# Two variants: inch-based (for new slides) and raw-EMU (for image replacements)

def _mk(oid, sid, shape_type, tx, ty, sx, sy):
    return {'createShape': {'objectId': oid, 'shapeType': shape_type,
        'elementProperties': {'pageObjectId': sid,
            'size': {'width': _v(BASE), 'height': _v(BASE)},
            'transform': {'scaleX': sx, 'scaleY': sy,
                          'translateX': int(tx), 'translateY': int(ty),
                          'unit': 'EMU'}}}}

def box(oid, sid, x, y, w, h):   # x,y,w,h in inches
    return _mk(oid, sid, 'TEXT_BOX',  emu(x), emu(y), emu(w)/BASE, emu(h)/BASE)
def rct(oid, sid, x, y, w, h):
    return _mk(oid, sid, 'RECTANGLE', emu(x), emu(y), emu(w)/BASE, emu(h)/BASE)
def box_r(oid, sid, tx, ty, sx, sy):   # raw EMU translate + raw scale
    return _mk(oid, sid, 'TEXT_BOX',  tx, ty, sx, sy)
def rct_r(oid, sid, tx, ty, sx, sy):
    return _mk(oid, sid, 'RECTANGLE', tx, ty, sx, sy)

# ── Text / style helpers ──────────────────────────────────────────────────────

def txt(oid, text):
    return {'insertText': {'objectId': oid, 'text': text, 'insertionIndex': 0}}

def tstyle(oid, bold=None, italic=None, size=None, color=None, font=None, s=None, e=None):
    st, flds = {}, []
    if bold    is not None: st['bold']   = bold;   flds.append('bold')
    if italic  is not None: st['italic'] = italic; flds.append('italic')
    if size    is not None: st['fontSize'] = _v(pt(size)); flds.append('fontSize')
    if color   is not None:
        st['foregroundColor'] = {'opaqueColor': {'rgbColor': color}}
        flds.append('foregroundColor')
    if font    is not None: st['fontFamily'] = font; flds.append('fontFamily')
    tr = {'type': 'ALL'} if s is None else {'type': 'FIXED_RANGE', 'startIndex': s, 'endIndex': e}
    return {'updateTextStyle': {'objectId': oid, 'style': st,
                                'textRange': tr, 'fields': ','.join(flds)}}

def algn(oid, a='START'):
    return {'updateParagraphStyle': {'objectId': oid,
            'style': {'alignment': a}, 'textRange': {'type': 'ALL'},
            'fields': 'alignment'}}

def sfill(oid, color=None, transparent=False):
    f = {'propertyState': 'NOT_RENDERED'} if transparent else \
        {'solidFill': {'color': {'rgbColor': color}}}
    return {'updateShapeProperties': {'objectId': oid,
            'shapeProperties': {'shapeBackgroundFill': f},
            'fields': 'shapeBackgroundFill'}}

def nborder(oid):
    return {'updateShapeProperties': {'objectId': oid,
            'shapeProperties': {'outline': {'propertyState': 'NOT_RENDERED'}},
            'fields': 'outline'}}

def sborder(oid, color, w_pt=1.5):
    return {'updateShapeProperties': {'objectId': oid,
            'shapeProperties': {'outline': {
                'outlineFill': {'solidFill': {'color': {'rgbColor': color}}},
                'weight': _v(pt(w_pt)), 'propertyState': 'RENDERED'}},
            'fields': 'outline'}}

def sbg(sid, color):
    return {'updatePageProperties': {'objectId': sid,
            'pageProperties': {'pageBackgroundFill':
                {'solidFill': {'color': {'rgbColor': color}}}},
            'fields': 'pageBackgroundFill'}}

def ctop(oid):
    return {'updateShapeProperties': {'objectId': oid,
            'shapeProperties': {'contentAlignment': 'TOP'},
            'fields': 'contentAlignment'}}

def clear_slide(svc, slide_id, slide_data):
    ids = [e['objectId'] for e in slide_data.get('pageElements', [])]
    if ids:
        batch(svc, [{'deleteObject': {'objectId': eid}} for eid in ids])
        print(f'  cleared {len(ids)} elements')


# ══════════════════════════════════════════════════════════════════════════════
# Product Roadmap  (13.33" wide)
# ══════════════════════════════════════════════════════════════════════════════

def build_roadmap(svc, sid):
    reqs = [sbg(sid, NAVY)]

    # Title row
    tid = _oid()
    reqs += [
        box(tid, sid, 0.55, 0.28, 12.23, 0.72),
        txt(tid, 'Product Roadmap'),
        tstyle(tid, bold=True, size=36, color=WHITE, font='Inter'),
        algn(tid, 'START'), sfill(tid, transparent=True), nborder(tid),
    ]

    bid = _oid()
    reqs += [
        rct(bid, sid, 0.55, 1.07, 1.5, 0.055),
        sfill(bid, GREEN), nborder(bid),
    ]

    # Column geometry (3 equal columns spanning full 13.33" width)
    margin = 0.55           # left/right margin
    gap    = 0.28           # gap between columns
    col_w  = (13.333 - 2*margin - 2*gap) / 3   # ≈ 3.9"
    col_xs = [margin,
              margin + col_w + gap,
              margin + 2*(col_w + gap)]
    c_top  = 1.22
    hdr_h  = 0.80
    gapv   = 0.06
    body_h = H/914_400 - c_top - hdr_h - gapv - 0.28   # ≈ 5.14"

    phases = [
        {'label': 'MVP',           'sub': 'Live Now',
         'items': ['Roster & Athlete Profiles',
                   'Coach-to-Parent Messaging',
                   'Scheduling & RSVP',
                   'Payments & Invoicing',
                   '4–5 pilot clubs · ~300 athletes']},
        {'label': 'Pilot Expansion','sub': '6 Months',
         'items': ['50–150 clubs onboarded',
                   'Multi-sport rollout',
                   'Android app launch',
                   'Growing payment volume',
                   'Club partnership program']},
        {'label': 'Full Launch',   'sub': '12–18 Months',
         'items': ['AI performance analytics',
                   'Game stats & highlights',
                   'Athlete recruiting profiles',
                   'Live streaming integration',
                   'Vendor marketplace · National scale']},
    ]

    for i, ph in enumerate(phases):
        x = col_xs[i]

        # Header card
        hid = _oid()
        reqs += [rct(hid, sid, x, c_top, col_w, hdr_h),
                 sfill(hid, DKNAVY), sborder(hid, GREEN, 1.5)]

        label, sub = ph['label'], ph['sub']
        merged = f'{label}\n{sub}'
        ll, tl = len(label), len(merged)
        htid = _oid()
        reqs += [
            box(htid, sid, x+0.18, c_top+0.10, col_w-0.36, hdr_h-0.20),
            txt(htid, merged),
            tstyle(htid, bold=True,  size=18, color=GREEN, font='Inter', s=0,    e=ll),
            tstyle(htid, bold=False, size=10, color=GRAY,  font='Inter', s=ll+1, e=tl),
            algn(htid, 'START'), sfill(htid, transparent=True), nborder(htid),
        ]

        # Body card
        by = c_top + hdr_h + gapv
        bkid = _oid()
        reqs += [rct(bkid, sid, x, by, col_w, body_h),
                 sfill(bkid, MDNAVY), sborder(bkid, BORD, 1)]

        btid     = _oid()
        body_txt = '\n'.join(f'  ●  {it}' for it in ph['items'])
        reqs    += [
            box(btid, sid, x+0.20, by+0.22, col_w-0.40, body_h-0.44),
            txt(btid, body_txt),
            tstyle(btid, bold=False, size=14, color=WHITE, font='Inter'),
            algn(btid, 'START'), sfill(btid, transparent=True), nborder(btid),
            ctop(btid),
        ]

    batch(svc, reqs)
    print('  ✓ Product Roadmap rebuilt')


# ══════════════════════════════════════════════════════════════════════════════
# Our Team  (13.33" wide, 2×2 grid)
# ══════════════════════════════════════════════════════════════════════════════

def build_team(svc, sid):
    reqs = [sbg(sid, NAVY)]

    # Title
    tid = _oid()
    reqs += [
        box(tid, sid, 0.55, 0.28, 12.23, 0.72),
        txt(tid, 'Our Team'),
        tstyle(tid, bold=True, size=36, color=WHITE, font='Inter'),
        algn(tid, 'START'), sfill(tid, transparent=True), nborder(tid),
    ]

    bid = _oid()
    reqs += [rct(bid, sid, 0.55, 1.07, 1.0, 0.055), sfill(bid, GREEN), nborder(bid)]

    members = [
        {'name': 'Aliza Avital-Caplan', 'role': 'Founder',
         'bio': '20-year real estate broker with $2.4B+ in sales. Mother of a '
                'competitive gymnast — built TeamThrive to solve the scheduling '
                'and communication chaos she lived every season.'},
        {'name': 'Courtney Guertin', 'role': 'Technical Advisor',
         'bio': 'Former CTO of Ease, scaled to 15M+ users and $100M+ raised. '
                'Expert in consumer-grade sports and wellness software at scale.'},
        {'name': 'Craig Zappa', 'role': 'Coach, Club Owner & Advisor',
         'bio': 'Owner of ENA Gymnastics with 38 years of coaching experience. '
                'Home to Olympian Olivia Dunne. Deep operator insight into what '
                'elite club programs need.'},
        {'name': 'Max Kothari', 'role': 'Web Developer & Analyst',
         'bio': 'Phillips Exeter Academy. Brings sharp analytical and full-stack '
                'technical skills to the team.'},
    ]

    # 2×2 layout spanning full 13.33" width
    margin  = 0.55
    gap_x   = 0.28
    card_w  = (13.333 - 2*margin - gap_x) / 2   # ≈ 5.96"
    card_h  = 2.72
    gap_y   = 0.22
    row_ys  = [1.3, 1.3 + card_h + gap_y]

    for i, m in enumerate(members):
        row = i // 2
        col = i  % 2
        x   = margin + col * (card_w + gap_x)
        y   = row_ys[row]
        pad = 0.24
        iw  = card_w - 2*pad

        cid = _oid()
        reqs += [rct(cid, sid, x, y, card_w, card_h),
                 sfill(cid, DKNAVY), sborder(cid, BORD, 1)]

        stid = _oid()
        sh   = 0.055
        reqs += [rct(stid, sid, x, y, card_w, sh), sfill(stid, GREEN), nborder(stid)]

        name_y  = y + sh + 0.14
        nid     = _oid()
        reqs   += [
            box(nid, sid, x+pad, name_y, iw, 0.44),
            txt(nid, m['name']),
            tstyle(nid, bold=True, size=15, color=WHITE, font='Inter'),
            algn(nid, 'START'), sfill(nid, transparent=True), nborder(nid),
        ]

        role_y = name_y + 0.44 + 0.06
        rid    = _oid()
        reqs  += [
            box(rid, sid, x+pad, role_y, iw, 0.38),
            txt(rid, m['role']),
            tstyle(rid, bold=False, size=11, color=GREEN, font='Inter'),
            algn(rid, 'START'), sfill(rid, transparent=True), nborder(rid),
        ]

        div_y = role_y + 0.38 + 0.10
        did   = _oid()
        reqs += [rct(did, sid, x+pad, div_y, iw, 0.012),
                 sfill(did, BORD), nborder(did)]

        bio_y = div_y + 0.012 + 0.10
        bio_h = (y + card_h) - bio_y - 0.12
        bioid = _oid()
        reqs += [
            box(bioid, sid, x+pad, bio_y, iw, bio_h),
            txt(bioid, m['bio']),
            tstyle(bioid, bold=False, size=11, color=BLUGRAY, font='Inter'),
            algn(bioid, 'START'), sfill(bioid, transparent=True), nborder(bioid),
            ctop(bioid),
        ]

    batch(svc, reqs)
    print('  ✓ Our Team rebuilt')


# ══════════════════════════════════════════════════════════════════════════════
# Broken image replacement
# ══════════════════════════════════════════════════════════════════════════════

def replace_large_image(svc, sid, img_id, tx, ty, sx, sy, emoji, title, desc):
    """Delete a broken screenshot image; insert a styled dark placeholder."""
    batch(svc, [{'deleteObject': {'objectId': img_id}}])

    vw = BASE * sx   # visual width  (EMU)
    vh = BASE * sy   # visual height (EMU)

    reqs = []

    # Dark background rectangle (same size/position as original image)
    bg_id = _oid()
    reqs += [rct_r(bg_id, sid, tx, ty, sx, sy),
             sfill(bg_id, DARKCARD), nborder(bg_id)]

    # Emoji — large, centered, top 45% of area
    em_id = _oid()
    em_tx = tx + int(vw * 0.10)
    em_ty = ty + int(vh * 0.08)
    em_sx = vw * 0.80 / BASE
    em_sy = vh * 0.42 / BASE
    reqs += [
        box_r(em_id, sid, em_tx, em_ty, em_sx, em_sy),
        txt(em_id, emoji),
        tstyle(em_id, size=50, color=GREEN),
        algn(em_id, 'CENTER'),
        sfill(em_id, transparent=True), nborder(em_id),
    ]

    # Feature title
    t_id = _oid()
    t_tx = tx + int(vw * 0.06)
    t_ty = ty + int(vh * 0.52)
    t_sx = vw * 0.88 / BASE
    t_sy = vh * 0.17 / BASE
    reqs += [
        box_r(t_id, sid, t_tx, t_ty, t_sx, t_sy),
        txt(t_id, title),
        tstyle(t_id, bold=True, size=11, color=GREEN, font='Inter'),
        algn(t_id, 'CENTER'),
        sfill(t_id, transparent=True), nborder(t_id),
    ]

    # Description
    d_id = _oid()
    d_tx = tx + int(vw * 0.06)
    d_ty = ty + int(vh * 0.70)
    d_sx = vw * 0.88 / BASE
    d_sy = vh * 0.22 / BASE
    reqs += [
        box_r(d_id, sid, d_tx, d_ty, d_sx, d_sy),
        txt(d_id, desc),
        tstyle(d_id, bold=False, size=10, color=BLUGRAY, font='Inter'),
        algn(d_id, 'CENTER'),
        sfill(d_id, transparent=True), nborder(d_id),
    ]

    batch(svc, reqs)
    print(f'    ✓ {img_id} → {emoji} "{title}"')


def replace_small_icon(svc, sid, img_id, tx, ty, sx, sy, emoji, font_pt=16,
                       color=None):
    """Delete a broken small icon; insert a centered emoji text box."""
    batch(svc, [{'deleteObject': {'objectId': img_id}}])

    ic_id = _oid()
    c     = color or GREEN
    batch(svc, [
        box_r(ic_id, sid, tx, ty, sx, sy),
        txt(ic_id, emoji),
        tstyle(ic_id, size=font_pt, color=c),
        algn(ic_id, 'CENTER'),
        sfill(ic_id, transparent=True), nborder(ic_id),
    ])
    print(f'    ✓ {img_id} → {emoji} (icon)')


def fix_broken_images(svc):
    # ── Slide 16 (p16): Revenue Model — 5 pentagon icons ─────────────────────
    print('  Slide 16: Revenue Model icons...')
    s16 = 'p16'
    icons16 = [
        # (img_id,   tx,      ty,      sx,     sy,     emoji, pt)
        ('p16_i58', 5909623, 2299059, 0.1393, 0.1393, '✨', 18),
        ('p16_i60', 4516616, 3391175, 0.1249, 0.1249, '⚡', 16),
        ('p16_i62', 5006113, 5053201, 0.1640, 0.1640, '📢', 18),
        ('p16_i64', 6787865, 5106494, 0.1381, 0.1381, '👑', 18),
        ('p16_i66', 7288234, 3344503, 0.1654, 0.1654, '👤', 18),
    ]
    for img_id, tx, ty, sx, sy, emoji, fp in icons16:
        replace_small_icon(svc, s16, img_id, tx, ty, sx, sy, emoji, font_pt=fp)

    # ── Slide 19 (p19): Unit Economics — 2 gradient box icons ─────────────────
    print('  Slide 19: Unit Economics icons...')
    s19 = 'p19'
    icons19 = [
        ('p19_i45', 1549809, 4708654, 0.1202, 0.1202, '%',  18, DKNAVY),
        ('p19_i47', 7535266, 4743145, 0.0972, 0.0972, '↑', 16, DKNAVY),
    ]
    for img_id, tx, ty, sx, sy, emoji, fp, col in icons19:
        replace_small_icon(svc, s19, img_id, tx, ty, sx, sy, emoji, font_pt=fp, color=col)

    # ── Slide 29 (p28): Operations — 2 large screenshot areas ─────────────────
    print('  Slide 29 (Operations): large screenshots...')
    replace_large_image(svc, 'p28', 'p28_i54',
        1579419, 2491906, 1.0714, 0.8522,
        '📋', 'ROSTER MANAGEMENT',
        'Athletes · Attendance · Schedules')
    replace_large_image(svc, 'p28', 'p28_i56',
        7496958, 2413007, 1.0047, 0.8512,
        '💬', 'TEAM COMMUNICATION',
        'Messaging · Announcements · Chats')

    # ── Slide 30 (p29): Performance — 3 large screenshot areas ────────────────
    print('  Slide 30 (Performance): large screenshots...')
    replace_large_image(svc, 'p29', 'p29_i20',
        638464, 2595418, 1.0668, 0.8068,
        '📊', 'GAME STATS & RECAPS',
        'Track performance · Key moments')
    replace_large_image(svc, 'p29', 'p29_i24',
        4950423, 2401361, 0.7760, 0.8623,
        '⚽', 'DRILLS & PRACTICE',
        'Pro coach skill-building drills')
    replace_large_image(svc, 'p29', 'p29_i19',
        8869452, 2595418, 0.7659, 0.7650,
        '✨', 'AI ANALYSIS',
        'Video · Technique · Progress')

    # ── Slide 31 (p30): Recruitment — 2 large screenshot areas ────────────────
    print('  Slide 31 (Recruitment): large screenshots...')
    replace_large_image(svc, 'p30', 'p30_i11',
        1466035, 2533534, 1.1246, 0.8391,
        '🎥', 'BUILT-IN LIVE STREAMING',
        'Stream games for families & recruiters')
    replace_large_image(svc, 'p30', 'p30_i17',
        7570467, 2533533, 0.9543, 0.8356,
        '🏅', 'ATHLETE PROFILES',
        'Stats · Highlights · Recruiting tools')


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    svc = get_service()

    print('Reading presentation...')
    pres   = get_pres(svc)
    slides = pres['slides']
    smap   = {s['objectId']: s for s in slides}
    print(f'  {len(slides)} slides, canvas {W}×{H} EMU\n')

    # 1. Product Roadmap
    if ROADMAP_ID in smap:
        print(f'Rebuilding Product Roadmap...')
        clear_slide(svc, ROADMAP_ID, smap[ROADMAP_ID])
        build_roadmap(svc, ROADMAP_ID)
    else:
        print(f'ERROR: roadmap slide not found')

    # 2. Our Team
    if TEAM_ID in smap:
        print(f'\nRebuilding Our Team...')
        clear_slide(svc, TEAM_ID, smap[TEAM_ID])
        build_team(svc, TEAM_ID)
    else:
        print(f'ERROR: team slide not found')

    # 3. Broken images
    print(f'\nFixing broken images...')
    fix_broken_images(svc)

    print('\n✅  All done!')
    print(f'   https://docs.google.com/presentation/d/{PRESENTATION_ID}/edit')


if __name__ == '__main__':
    main()
