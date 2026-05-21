#!/usr/bin/env python3
"""Add Ronas IT development-partner card to slide 36 (Our Team) in Google Slides."""

import os, httplib2, google_auth_httplib2
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as SA

PRES  = '1nZ1YfTqSUfzsBbzZC8azxza9XoPZ66mfJI2fXHOwIIo'
SCOPES = ['https://www.googleapis.com/auth/presentations']

# Slide dimensions (EMU): 9144000 wide × 5143500 tall (widescreen 16:9)
W = 9144000
H = 5143500

# Card geometry — full-width banner near the bottom
MARGIN   = 457200   # ~0.5 in from left/right edges
CARD_X   = MARGIN
CARD_W   = W - 2 * MARGIN
CARD_Y   = 3962400  # ~4.33 in from top
CARD_H   = 950000   # ~1.04 in tall

def get_svc():
    key = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')
    creds = SA.from_service_account_file(key, scopes=SCOPES)
    h = httplib2.Http(ca_certs='/etc/ssl/certs/ca-certificates.crt')
    return build('slides', 'v1', http=google_auth_httplib2.AuthorizedHttp(creds, http=h))

def emu(pts):
    return int(pts * 12700)

def pt(emu_val):
    return emu_val / 12700

def batch(svc, reqs):
    if not reqs:
        print('  (nothing to send)')
        return
    resp = svc.presentations().batchUpdate(
        presentationId=PRES, body={'requests': reqs}).execute()
    print(f'  batchUpdate OK — {len(reqs)} request(s)')
    return resp

def shape_text(el):
    parts = []
    for te in el.get('shape', {}).get('text', {}).get('textElements', []):
        if 'textRun' in te:
            parts.append(te['textRun'].get('content', ''))
    return ''.join(parts)

def inspect_slide36(svc):
    pres = svc.presentations().get(presentationId=PRES).execute()
    slides = pres['slides']
    print(f'Total slides: {len(slides)}')
    slide = slides[35]   # 0-indexed → slide 36
    print(f'Slide 36 objectId: {slide["objectId"]}')
    bottom = 0
    for el in slide.get('pageElements', []):
        t = el.get('transform', {})
        sz = el.get('size', {})
        y  = t.get('translateY', 0)
        h  = sz.get('height', {}).get('magnitude', 0)
        bottom = max(bottom, y + h)
        txt = shape_text(el)[:60] if 'shape' in el else ''
        print(f'  {el["objectId"]:30s} y={pt(y):.0f}pt h={pt(h):.0f}pt | {repr(txt)}')
    print(f'\nBottom-most element ends at: {pt(bottom):.0f}pt from top')
    return slide['objectId'], bottom

def main():
    svc = get_svc()

    print('=== Inspecting slide 36 ===')
    slide_oid, bottom_emu = inspect_slide36(svc)

    # Place card 18pt below the bottom-most existing element, or use hardcoded CARD_Y
    # whichever is lower (larger y value)
    gap = emu(18)
    card_y = max(CARD_Y, bottom_emu + gap)
    print(f'\nPlacing Ronas IT card at y={pt(card_y):.0f}pt')

    reqs = []

    # ── Background card shape ─────────────────────────────────────────────────
    BG_OID   = 'ronas_bg_card'
    NAME_OID = 'ronas_name'
    DESC_OID = 'ronas_desc'
    LINK_OID = 'ronas_link'

    def mk_shape(oid, x, y, w, h):
        return {
            'createShape': {
                'objectId': oid,
                'shapeType': 'RECTANGLE',
                'elementProperties': {
                    'pageObjectId': slide_oid,
                    'size': {
                        'width':  {'magnitude': w, 'unit': 'EMU'},
                        'height': {'magnitude': h, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': x, 'translateY': y,
                        'unit': 'EMU'
                    }
                }
            }
        }

    # Full-width background card
    reqs.append(mk_shape(BG_OID, CARD_X, card_y, CARD_W, CARD_H))

    # Name + role block (left-ish, top part of card)
    name_x = CARD_X + emu(14)
    name_y = card_y + emu(14)
    name_w = emu(280)
    name_h = emu(52)
    reqs.append(mk_shape(NAME_OID, name_x, name_y, name_w, name_h))

    # Description (rest of width, full card height minus padding)
    desc_x = CARD_X + emu(14)
    desc_y = card_y + emu(52)
    desc_w = CARD_W - emu(28)
    desc_h = CARD_H - emu(66)
    reqs.append(mk_shape(DESC_OID, desc_x, desc_y, desc_w, desc_h))

    # Website link (top-right of card)
    link_x = CARD_X + CARD_W - emu(130)
    link_y = card_y + emu(14)
    link_w = emu(124)
    link_h = emu(24)
    reqs.append(mk_shape(LINK_OID, link_x, link_y, link_w, link_h))

    print(f'\nCreating shapes...')
    batch(svc, reqs)

    # ── Style shapes ─────────────────────────────────────────────────────────
    style_reqs = []

    def fill_shape(oid, r, g, b, a=1.0):
        return {
            'updateShapeProperties': {
                'objectId': oid,
                'fields': 'shapeBackgroundFill,outline',
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': {'red': r/255, 'green': g/255, 'blue': b/255}},
                            'alpha': a
                        }
                    },
                    'outline': {'propertyState': 'NOT_RENDERED'}
                }
            }
        }

    style_reqs.append(fill_shape(BG_OID,  30, 43, 74, 0.95))   # dark navy
    style_reqs.append(fill_shape(NAME_OID, 30, 43, 74, 0.0))    # transparent
    style_reqs.append(fill_shape(DESC_OID, 30, 43, 74, 0.0))    # transparent
    style_reqs.append(fill_shape(LINK_OID, 30, 43, 74, 0.0))    # transparent

    batch(svc, style_reqs)

    # ── Insert text ───────────────────────────────────────────────────────────
    text_reqs = []

    text_reqs.append({'insertText': {'objectId': NAME_OID, 'insertionIndex': 0,
        'text': 'Ronas IT  ·  Development Partner'}})

    desc = ('The Ronas team has been an exceptional development partner throughout '
            'the build — responsive, committed, and deeply invested in the '
            'long-term vision of Team Thrive. They don\'t just build features; '
            'they understand the mission and the impact this platform can have on '
            'competitive youth athletes, parents, and coaches. Their communication, '
            'problem-solving, and willingness to grow alongside the product have '
            'made them true partners — not just contractors.')
    text_reqs.append({'insertText': {'objectId': DESC_OID, 'insertionIndex': 0, 'text': desc}})
    text_reqs.append({'insertText': {'objectId': LINK_OID, 'insertionIndex': 0, 'text': 'ronasit.com'}})

    batch(svc, text_reqs)

    # ── Style text ────────────────────────────────────────────────────────────
    def rgb(r, g, b):
        return {'rgbColor': {'red': r/255, 'green': g/255, 'blue': b/255}}

    def text_style(oid, bold=False, size_pt=11, color=(255,255,255), start=0, end=None):
        req = {
            'updateTextStyle': {
                'objectId': oid,
                'style': {
                    'bold': bold,
                    'fontSize': {'magnitude': size_pt, 'unit': 'PT'},
                    'foregroundColor': {'opaqueColor': rgb(*color)},
                    'fontFamily': 'Barlow'
                },
                'fields': 'bold,fontSize,foregroundColor,fontFamily'
            }
        }
        if end is not None:
            req['updateTextStyle']['textRange'] = {
                'type': 'FIXED_RANGE', 'startIndex': start, 'endIndex': end}
        else:
            req['updateTextStyle']['textRange'] = {'type': 'ALL'}
        return req

    # Name line: "Ronas IT" bold teal, rest smaller grey
    ronas_label = 'Ronas IT  ·  Development Partner'
    text_reqs2 = [
        text_style(NAME_OID, bold=True,  size_pt=14, color=(43, 181, 160)),  # whole line teal first
        text_style(NAME_OID, bold=False, size_pt=11, color=(180, 190, 200),   # then dim the role part
                   start=len('Ronas IT'), end=len(ronas_label)),
        text_style(DESC_OID, bold=False, size_pt=10, color=(210, 220, 230)),
        text_style(LINK_OID, bold=False, size_pt=10, color=(43, 181, 160)),
    ]
    batch(svc, text_reqs2)

    # ── Add hyperlink to website ──────────────────────────────────────────────
    link_reqs = [{
        'updateTextStyle': {
            'objectId': LINK_OID,
            'style': {'link': {'url': 'http://ronasit.com'}},
            'fields': 'link',
            'textRange': {'type': 'ALL'}
        }
    }]
    batch(svc, link_reqs)

    print('\nDone — Ronas IT card added to slide 36.')

if __name__ == '__main__':
    main()
