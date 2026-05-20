#!/usr/bin/env python3
"""
Fix Team Thrive new slides:
  • Delete blank slide  id_20a16a35c8464377
  • Rebuild Product Roadmap   id_22682c1b6c814be1
  • Rebuild Our Team          id_28e03f1590b44fbb

Root-cause: Google Slides createShape ignores the 'size' field in
elementProperties.  Actual visual dimensions are controlled by scaleX/scaleY
in the AffineTransform, where:
    visual_width  = 3_000_000 EMU × scaleX
    visual_height = 3_000_000 EMU × scaleY
"""

import os
import sys
import uuid
import httplib2
import google_auth_httplib2
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as SACredentials

PRESENTATION_ID = '1FNIUCC8jPqpwL8xTrQ33J3vGFwuaULhyp_BknKOuIjk'
SCOPES = ['https://www.googleapis.com/auth/presentations']

BLANK_SLIDE_ID   = 'id_20a16a35c8464377'
ROADMAP_SLIDE_ID = 'id_22682c1b6c814be1'
TEAM_SLIDE_ID    = 'id_28e03f1590b44fbb'

# ── Colours ───────────────────────────────────────────────────────────────────

def rgb(h):
    h = h.lstrip('#')
    return {'red': int(h[0:2], 16)/255, 'green': int(h[2:4], 16)/255, 'blue': int(h[4:6], 16)/255}

NAVY   = rgb('0D1B3E')
GREEN  = rgb('3DDC84')
WHITE  = {'red': 1.0, 'green': 1.0, 'blue': 1.0}
GRAY   = rgb('8892A4')
DKNAVY = rgb('08122A')
MDNAVY = rgb('0F2347')
BLUGRAY = rgb('B0BCCC')
BORD   = rgb('1C3060')

# ── Units ─────────────────────────────────────────────────────────────────────

def emu(inches):   return int(inches * 914_400)
def pt(points):    return int(points * 12_700)
def _v(v):         return {'magnitude': v, 'unit': 'EMU'}

BASE = 3_000_000   # Google Slides base size for all shapes (EMU)
W    = emu(10)     # slide width
H    = emu(7.5)    # slide height

# ── Auth ─────────────────────────────────────────────────────────────────────

def get_service():
    ca = os.environ.get('REQUESTS_CA_BUNDLE', '/etc/ssl/certs/ca-certificates.crt')
    key = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')
    if not os.path.exists(key):
        sys.exit(f'Key file not found: {key}')
    creds = SACredentials.from_service_account_file(key, scopes=SCOPES)
    h = httplib2.Http(ca_certs=ca)
    return build('slides', 'v1', http=google_auth_httplib2.AuthorizedHttp(creds, http=h))

def get_pres(svc):
    return svc.presentations().get(presentationId=PRESENTATION_ID).execute()

def batch(svc, requests):
    if not requests:
        return
    return svc.presentations().batchUpdate(
        presentationId=PRESENTATION_ID, body={'requests': requests}
    ).execute()

def _oid():
    return 'fix_' + uuid.uuid4().hex[:16]

# ── Shape creation (correct sizing via scaleX/scaleY) ────────────────────────

def _shape(obj_id, slide_id, shape_type, x, y, w, h):
    return {
        'createShape': {
            'objectId': obj_id,
            'shapeType': shape_type,
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {'width': _v(BASE), 'height': _v(BASE)},
                'transform': {
                    'scaleX': w / BASE,
                    'scaleY': h / BASE,
                    'translateX': x,
                    'translateY': y,
                    'unit': 'EMU',
                },
            },
        }
    }

def box(oid, sid, x, y, w, h):   return _shape(oid, sid, 'TEXT_BOX',  x, y, w, h)
def rect(oid, sid, x, y, w, h):  return _shape(oid, sid, 'RECTANGLE', x, y, w, h)

# ── Text / style helpers ──────────────────────────────────────────────────────

def txt(oid, text):
    return {'insertText': {'objectId': oid, 'text': text, 'insertionIndex': 0}}

def tstyle(oid, bold=None, italic=None, size=None, color=None, font=None,
           s=None, e=None):
    st, flds = {}, []
    if bold    is not None: st['bold']   = bold;   flds.append('bold')
    if italic  is not None: st['italic'] = italic; flds.append('italic')
    if size    is not None: st['fontSize'] = _v(pt(size)); flds.append('fontSize')
    if color   is not None:
        st['foregroundColor'] = {'opaqueColor': {'rgbColor': color}}
        flds.append('foregroundColor')
    if font    is not None: st['fontFamily'] = font; flds.append('fontFamily')
    tr = {'type': 'ALL'} if s is None else {'type': 'FIXED_RANGE', 'startIndex': s, 'endIndex': e}
    return {'updateTextStyle': {'objectId': oid, 'style': st, 'textRange': tr,
                                'fields': ','.join(flds)}}

def align(oid, a='START'):
    return {'updateParagraphStyle': {'objectId': oid,
            'style': {'alignment': a}, 'textRange': {'type': 'ALL'},
            'fields': 'alignment'}}

def fill(oid, color=None, transparent=False):
    f = {'propertyState': 'NOT_RENDERED'} if transparent else \
        {'solidFill': {'color': {'rgbColor': color}}}
    return {'updateShapeProperties': {'objectId': oid,
            'shapeProperties': {'shapeBackgroundFill': f},
            'fields': 'shapeBackgroundFill'}}

def border(oid, color=None, weight=1.5, hide=False):
    if hide:
        ol = {'propertyState': 'NOT_RENDERED'}
    else:
        ol = {'outlineFill': {'solidFill': {'color': {'rgbColor': color}}},
              'weight': _v(pt(weight)), 'propertyState': 'RENDERED'}
    return {'updateShapeProperties': {'objectId': oid,
            'shapeProperties': {'outline': ol}, 'fields': 'outline'}}

def bg(sid, color):
    return {'updatePageProperties': {'objectId': sid,
            'pageProperties': {'pageBackgroundFill':
                {'solidFill': {'color': {'rgbColor': color}}}},
            'fields': 'pageBackgroundFill'}}

def content_top(oid):
    return {'updateShapeProperties': {'objectId': oid,
            'shapeProperties': {'contentAlignment': 'TOP'},
            'fields': 'contentAlignment'}}

# ── Slide helpers ─────────────────────────────────────────────────────────────

def clear_slide(svc, slide_id, slide_data):
    elems = [e['objectId'] for e in slide_data.get('pageElements', [])]
    if elems:
        batch(svc, [{'deleteObject': {'objectId': eid}} for eid in elems])
        print(f'  cleared {len(elems)} elements from {slide_id}')

# ─────────────────────────────────────────────────────────────────────────────
# Product Roadmap
# ─────────────────────────────────────────────────────────────────────────────

def build_roadmap(svc, sid):
    reqs = [bg(sid, NAVY)]

    # ── Title ────────────────────────────────────────────────────────────────
    tid = _oid()
    reqs += [
        box(tid, sid, emu(0.48), emu(0.28), emu(9.04), emu(0.7)),
        txt(tid, 'Product Roadmap'),
        tstyle(tid, bold=True, size=34, color=WHITE, font='Inter'),
        align(tid), fill(tid, transparent=True), border(tid, hide=True),
    ]

    # Green accent bar under title
    bid = _oid()
    reqs += [
        rect(bid, sid, emu(0.48), emu(1.05), emu(1.5), emu(0.055)),
        fill(bid, GREEN), border(bid, hide=True),
    ]

    # ── 3 columns ────────────────────────────────────────────────────────────
    col_w  = emu(2.88)
    col_xs = [emu(0.48), emu(3.56), emu(6.64)]
    c_top  = emu(1.22)
    hdr_h  = emu(0.82)
    body_h = emu(5.62)   # c_top + hdr_h + body_h = 1.22+0.82+5.62 = 7.66 > 7.5 → trim

    # Recalculate: available vertical = 7.5 - 1.22 - 0.05 = 6.23"
    hdr_h  = emu(0.80)
    gap    = emu(0.06)
    body_h = emu(5.30)   # 1.22 + 0.80 + 0.06 + 5.30 = 7.38 < 7.5 ✓

    phases = [
        {
            'label': 'MVP',
            'sub':   'Live Now',
            'items': [
                'Roster & Athlete Profiles',
                'Coach-to-Parent Messaging',
                'Scheduling & RSVP',
                'Payments & Invoicing',
                '4–5 pilot clubs · ~300 athletes',
            ],
        },
        {
            'label': 'Pilot Expansion',
            'sub':   '6 Months',
            'items': [
                '50–150 clubs onboarded',
                'Multi-sport rollout',
                'Android app launch',
                'Growing payment volume',
                'Club partnership program',
            ],
        },
        {
            'label': 'Full Launch',
            'sub':   '12–18 Months',
            'items': [
                'AI performance analytics',
                'Game stats & highlights',
                'Athlete recruiting profiles',
                'Live streaming integration',
                'Vendor marketplace · National scale',
            ],
        },
    ]

    for i, ph in enumerate(phases):
        x = col_xs[i]

        # Header card background
        hid = _oid()
        reqs += [
            rect(hid, sid, x, c_top, col_w, hdr_h),
            fill(hid, DKNAVY), border(hid, GREEN, 1.5),
        ]

        # Header text: label + newline + sub
        label, sub = ph['label'], ph['sub']
        combined   = f'{label}\n{sub}'
        ll, tl     = len(label), len(combined)

        htid = _oid()
        reqs += [
            box(htid, sid, x + emu(0.14), c_top + emu(0.08),
                col_w - emu(0.28), hdr_h - emu(0.16)),
            txt(htid, combined),
            tstyle(htid, bold=True, size=16, color=GREEN, font='Inter', s=0,  e=ll),
            tstyle(htid, bold=False, size=10, color=GRAY, font='Inter', s=ll+1, e=tl),
            align(htid), fill(htid, transparent=True), border(htid, hide=True),
        ]

        # Body card background
        body_y = c_top + hdr_h + gap
        bkid = _oid()
        reqs += [
            rect(bkid, sid, x, body_y, col_w, body_h),
            fill(bkid, MDNAVY), border(bkid, BORD, 1),
        ]

        # Bullet items
        btid = _oid()
        body_txt = '\n'.join(f'  ●  {it}' for it in ph['items'])
        inner_h  = body_h - emu(0.36)
        reqs += [
            box(btid, sid, x + emu(0.14), body_y + emu(0.2),
                col_w - emu(0.28), inner_h),
            txt(btid, body_txt),
            tstyle(btid, bold=False, size=13, color=WHITE, font='Inter'),
            align(btid), fill(btid, transparent=True), border(btid, hide=True),
            content_top(btid),
        ]

    batch(svc, reqs)
    print('  ✓ Product Roadmap rebuilt')


# ─────────────────────────────────────────────────────────────────────────────
# Our Team  (2 × 2 grid — more horizontal space per card, cleaner bios)
# ─────────────────────────────────────────────────────────────────────────────

def build_team(svc, sid):
    reqs = [bg(sid, NAVY)]

    # ── Title ────────────────────────────────────────────────────────────────
    tid = _oid()
    reqs += [
        box(tid, sid, emu(0.48), emu(0.28), emu(9.04), emu(0.7)),
        txt(tid, 'Our Team'),
        tstyle(tid, bold=True, size=34, color=WHITE, font='Inter'),
        align(tid), fill(tid, transparent=True), border(tid, hide=True),
    ]

    # Green accent bar
    bid = _oid()
    reqs += [
        rect(bid, sid, emu(0.48), emu(1.05), emu(1.0), emu(0.055)),
        fill(bid, GREEN), border(bid, hide=True),
    ]

    members = [
        {
            'name': 'Aliza Avital-Caplan',
            'role': 'Founder',
            'bio': (
                '20-year real estate broker with $2.4B+ in sales. '
                'Mother of a competitive gymnast — built TeamThrive to solve '
                'the scheduling and communication chaos she lived every season.'
            ),
        },
        {
            'name': 'Courtney Guertin',
            'role': 'Technical Advisor',
            'bio': (
                'Former CTO of Ease, scaled to 15M+ users and $100M+ raised. '
                'Expert in consumer-grade sports and wellness software at scale.'
            ),
        },
        {
            'name': 'Craig Zappa',
            'role': 'Coach, Club Owner & Advisor',
            'bio': (
                'Owner of ENA Gymnastics with 38 years of coaching experience. '
                'Home to Olympian Olivia Dunne. '
                'Deep operator insight into what elite club programs need.'
            ),
        },
        {
            'name': 'Max Kothari',
            'role': 'Web Developer & Analyst',
            'bio': (
                'Phillips Exeter Academy. '
                'Brings sharp analytical and full-stack technical skills to the team.'
            ),
        },
    ]

    # 2 × 2 grid
    card_w  = emu(4.52)
    card_h  = emu(2.62)
    gap_x   = emu(0.16)
    gap_y   = emu(0.18)
    margin_x = (W - 2 * card_w - gap_x) // 2   # ≈ emu(0.4)
    row_y   = [emu(1.28), emu(1.28) + card_h + gap_y]

    for i, m in enumerate(members):
        row = i // 2
        col = i  % 2
        x   = margin_x + col * (card_w + gap_x)
        y   = row_y[row]
        pad = emu(0.18)
        iw  = card_w - 2 * pad      # inner content width

        # Card background
        cid = _oid()
        reqs += [
            rect(cid, sid, x, y, card_w, card_h),
            fill(cid, DKNAVY), border(cid, BORD, 1),
        ]

        # Green top accent strip
        stid = _oid()
        strip_h = emu(0.055)
        reqs += [
            rect(stid, sid, x, y, card_w, strip_h),
            fill(stid, GREEN), border(stid, hide=True),
        ]

        # Name
        name_y  = y + strip_h + emu(0.12)
        name_h  = emu(0.42)
        nid     = _oid()
        reqs += [
            box(nid, sid, x + pad, name_y, iw, name_h),
            txt(nid, m['name']),
            tstyle(nid, bold=True, size=14, color=WHITE, font='Inter'),
            align(nid), fill(nid, transparent=True), border(nid, hide=True),
        ]

        # Role
        role_y = name_y + name_h + emu(0.05)
        role_h = emu(0.38)
        rid    = _oid()
        reqs += [
            box(rid, sid, x + pad, role_y, iw, role_h),
            txt(rid, m['role']),
            tstyle(rid, bold=False, size=11, color=GREEN, font='Inter'),
            align(rid), fill(rid, transparent=True), border(rid, hide=True),
        ]

        # Divider
        div_y  = role_y + role_h + emu(0.09)
        div_h  = emu(0.012)
        did    = _oid()
        reqs += [
            rect(did, sid, x + pad, div_y, iw, div_h),
            fill(did, BORD), border(did, hide=True),
        ]

        # Bio — fills remaining card space minus bottom padding
        bio_y  = div_y + div_h + emu(0.09)
        bio_h  = (y + card_h) - bio_y - emu(0.12)
        bioid  = _oid()
        reqs += [
            box(bioid, sid, x + pad, bio_y, iw, bio_h),
            txt(bioid, m['bio']),
            tstyle(bioid, bold=False, size=11, color=BLUGRAY, font='Inter'),
            align(bioid), fill(bioid, transparent=True), border(bioid, hide=True),
            content_top(bioid),
        ]

    batch(svc, reqs)
    print('  ✓ Our Team slide rebuilt')


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    svc = get_service()

    print('Reading presentation...')
    pres   = get_pres(svc)
    slides = pres['slides']
    smap   = {s['objectId']: s for s in slides}
    print(f'  {len(slides)} slides total\n')

    # 1. Delete blank slide
    if BLANK_SLIDE_ID in smap:
        print(f'Deleting blank slide {BLANK_SLIDE_ID}...')
        batch(svc, [{'deleteObject': {'objectId': BLANK_SLIDE_ID}}])
        print('  ✓ done')
    else:
        print(f'  Blank slide already gone: {BLANK_SLIDE_ID}')

    # Re-read
    pres   = get_pres(svc)
    slides = pres['slides']
    smap   = {s['objectId']: s for s in slides}

    # 2. Product Roadmap
    if ROADMAP_SLIDE_ID in smap:
        print(f'\nRebuilding Product Roadmap ({ROADMAP_SLIDE_ID})...')
        clear_slide(svc, ROADMAP_SLIDE_ID, smap[ROADMAP_SLIDE_ID])
        build_roadmap(svc, ROADMAP_SLIDE_ID)
    else:
        print(f'  ERROR: roadmap slide not found ({ROADMAP_SLIDE_ID})')

    # 3. Our Team
    if TEAM_SLIDE_ID in smap:
        print(f'\nRebuilding Our Team ({TEAM_SLIDE_ID})...')
        clear_slide(svc, TEAM_SLIDE_ID, smap[TEAM_SLIDE_ID])
        build_team(svc, TEAM_SLIDE_ID)
    else:
        print(f'  ERROR: team slide not found ({TEAM_SLIDE_ID})')

    print('\n✅  Done!')
    print(f'   https://docs.google.com/presentation/d/{PRESENTATION_ID}/edit')


if __name__ == '__main__':
    main()
