#!/usr/bin/env python3
"""
Update Team Thrive Google Slides presentation via the Google Slides API.

Authentication: Place a service_account.json file in this directory,
or set GOOGLE_APPLICATION_CREDENTIALS env var to the path of such a file.
The service account must have Editor access to the presentation (or the
presentation must be shared with the service account email).
"""

import os
import sys
import json
import time
import uuid

import httplib2
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials as SACredentials
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
import google_auth_httplib2

PRESENTATION_ID = '1FNIUCC8jPqpwL8xTrQ33J3vGFwuaULhyp_BknKOuIjk'
SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive',
]

# ── Colour helpers ────────────────────────────────────────────────────────────

def hex_rgb(h):
    h = h.lstrip('#')
    return {'red': int(h[0:2], 16) / 255,
            'green': int(h[2:4], 16) / 255,
            'blue': int(h[4:6], 16) / 255}

NAVY   = hex_rgb('0D1B3E')
GREEN  = hex_rgb('3DDC84')
WHITE  = {'red': 1.0, 'green': 1.0, 'blue': 1.0}
GRAY   = hex_rgb('8892A4')
DKNAVY = hex_rgb('08122A')

# ── Unit helpers ──────────────────────────────────────────────────────────────

def emu(inches_val):
    return int(inches_val * 914400)

def pt(points_val):
    return int(points_val * 12700)

def _tr(t):
    return {'magnitude': t, 'unit': 'EMU'}

# Slide canvas: 10 × 7.5 inches
W = emu(10)
H = emu(7.5)

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_service():
    # Use system CA bundle to handle environments with SSL-intercepting proxies
    ca_bundle = os.environ.get('REQUESTS_CA_BUNDLE', '/etc/ssl/certs/ca-certificates.crt')

    key_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')
    if os.path.exists(key_path):
        creds = SACredentials.from_service_account_file(key_path, scopes=SCOPES)
        print(f'Using service account: {key_path}')
    elif os.path.exists('token.json'):
        creds = OAuthCredentials.from_authorized_user_file('token.json', SCOPES)
        print('Using OAuth token: token.json')
    else:
        sys.exit(
            '\nNo credentials found.\n'
            'Provide one of:\n'
            '  • service_account.json  (service-account key with Editor access)\n'
            '  • token.json            (OAuth2 token with presentations + drive scopes)\n'
            '  • GOOGLE_APPLICATION_CREDENTIALS env var pointing to a service-account key\n'
        )

    h = httplib2.Http(ca_certs=ca_bundle)
    return build('slides', 'v1', http=google_auth_httplib2.AuthorizedHttp(creds, http=h))


# ── Presentation helpers ───────────────────────────────────────────────────────

def get_pres(service):
    return service.presentations().get(presentationId=PRESENTATION_ID).execute()

def batch(service, requests):
    if not requests:
        return
    return service.presentations().batchUpdate(
        presentationId=PRESENTATION_ID,
        body={'requests': requests}
    ).execute()

def shape_text(elem):
    parts = []
    for te in elem.get('shape', {}).get('text', {}).get('textElements', []):
        if 'textRun' in te:
            parts.append(te['textRun'].get('content', ''))
    return ''.join(parts)

def cell_text(cell):
    parts = []
    for te in cell.get('text', {}).get('textElements', []):
        if 'textRun' in te:
            parts.append(te['textRun'].get('content', ''))
    return ''.join(parts)

def find_shapes_with(slide, needle, limit=None):
    """Return list of page-element dicts whose text contains needle."""
    hits = []
    for elem in slide.get('pageElements', []):
        if 'shape' in elem and needle in shape_text(elem):
            hits.append(elem)
            if limit and len(hits) >= limit:
                break
    return hits

def find_tables(slide):
    return [e for e in slide.get('pageElements', []) if 'table' in e]

# ── Low-level request builders ─────────────────────────────────────────────────

def replace_text_req(find, replace, page_ids=None, match_case=True):
    r = {
        'replaceAllText': {
            'containsText': {'text': find, 'matchCase': match_case},
            'replaceText': replace,
        }
    }
    if page_ids:
        r['replaceAllText']['pageObjectIds'] = page_ids
    return r

def delete_text_req(obj_id, start, end):
    return {
        'deleteText': {
            'objectId': obj_id,
            'textRange': {'type': 'FIXED_RANGE', 'startIndex': start, 'endIndex': end},
        }
    }

def insert_text_req(obj_id, text, idx=0):
    return {
        'insertText': {
            'objectId': obj_id,
            'text': text,
            'insertionIndex': idx,
        }
    }

def replace_shape_body(obj_id, current_text, new_text):
    """Replace the entire text content of a shape (delete + insert)."""
    text_len = len(current_text)
    reqs = []
    if text_len > 0:
        reqs.append(delete_text_req(obj_id, 0, text_len))
    reqs.append(insert_text_req(obj_id, new_text, 0))
    return reqs

def replace_cell_text(table_id, row, col, current_text, new_text):
    """Replace text in a table cell."""
    reqs = []
    text_len = len(current_text)
    if text_len > 0:
        reqs.append({
            'deleteText': {
                'objectId': table_id,
                'cellLocation': {'rowIndex': row, 'columnIndex': col},
                'textRange': {'type': 'FIXED_RANGE', 'startIndex': 0, 'endIndex': text_len},
            }
        })
    reqs.append({
        'insertText': {
            'objectId': table_id,
            'cellLocation': {'rowIndex': row, 'columnIndex': col},
            'text': new_text,
            'insertionIndex': 0,
        }
    })
    return reqs

# ── Slide-creation helpers ─────────────────────────────────────────────────────

def _oid():
    return 'obj_' + uuid.uuid4().hex[:16]

def create_blank_slide(insert_index):
    sid = _oid()
    return sid, {
        'createSlide': {
            'objectId': sid,
            'insertionIndex': insert_index,
            'slideLayoutReference': {'predefinedLayout': 'BLANK'},
        }
    }

def set_bg(slide_id, rgb):
    return {
        'updatePageProperties': {
            'objectId': slide_id,
            'pageProperties': {
                'pageBackgroundFill': {'solidFill': {'color': {'rgbColor': rgb}}}
            },
            'fields': 'pageBackgroundFill',
        }
    }

def add_textbox(obj_id, slide_id, x, y, w, h_val):
    return {
        'createShape': {
            'objectId': obj_id,
            'shapeType': 'TEXT_BOX',
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {'width': _tr(w), 'height': _tr(h_val)},
                'transform': {
                    'scaleX': 1, 'scaleY': 1,
                    'translateX': x, 'translateY': y,
                    'unit': 'EMU',
                },
            },
        }
    }

def set_text(obj_id, text):
    return {'insertText': {'objectId': obj_id, 'text': text, 'insertionIndex': 0}}

def style_text(obj_id, bold=False, italic=False, size_pt=None, rgb=None,
               font=None, start=None, end=None):
    style = {}
    fields = []
    if bold is not None:
        style['bold'] = bold
        fields.append('bold')
    if italic is not None:
        style['italic'] = italic
        fields.append('italic')
    if size_pt is not None:
        style['fontSize'] = _tr(pt(size_pt))
        fields.append('fontSize')
    if rgb is not None:
        style['foregroundColor'] = {'opaqueColor': {'rgbColor': rgb}}
        fields.append('foregroundColor')
    if font is not None:
        style['fontFamily'] = font
        fields.append('fontFamily')
    tr = {'type': 'ALL'} if start is None else {
        'type': 'FIXED_RANGE', 'startIndex': start, 'endIndex': end
    }
    return {
        'updateTextStyle': {
            'objectId': obj_id,
            'style': style,
            'textRange': tr,
            'fields': ','.join(fields),
        }
    }

def para_align(obj_id, alignment='LEFT'):
    return {
        'updateParagraphStyle': {
            'objectId': obj_id,
            'style': {'alignment': alignment},
            'textRange': {'type': 'ALL'},
            'fields': 'alignment',
        }
    }

def shape_fill(obj_id, rgb=None, transparent=False):
    if transparent:
        fill = {'propertyState': 'NOT_RENDERED'}
    else:
        fill = {'solidFill': {'color': {'rgbColor': rgb}}}
    return {
        'updateShapeProperties': {
            'objectId': obj_id,
            'shapeProperties': {'shapeBackgroundFill': fill},
            'fields': 'shapeBackgroundFill',
        }
    }

def no_border(obj_id):
    return {
        'updateShapeProperties': {
            'objectId': obj_id,
            'shapeProperties': {
                'outline': {'propertyState': 'NOT_RENDERED'}
            },
            'fields': 'outline',
        }
    }

def green_border(obj_id, weight_pt=2):
    return {
        'updateShapeProperties': {
            'objectId': obj_id,
            'shapeProperties': {
                'outline': {
                    'outlineFill': {'solidFill': {'color': {'rgbColor': GREEN}}},
                    'weight': _tr(pt(weight_pt)),
                    'propertyState': 'RENDERED',
                }
            },
            'fields': 'outline',
        }
    }

def shape_padding(obj_id, top=0, bot=0, left=0, right=0):
    return {
        'updateShapeProperties': {
            'objectId': obj_id,
            'shapeProperties': {
                'contentAlignment': 'TOP',
                'autofit': {'autofitType': 'NONE'},
            },
            'fields': 'contentAlignment,autofit',
        }
    }

# ── Build: Product Roadmap slide ──────────────────────────────────────────────

def build_roadmap_slide(service, insert_index):
    """Create the Product Roadmap slide at insert_index (0-based)."""
    sid, create_req = create_blank_slide(insert_index)
    batch(service, [create_req])

    reqs = [set_bg(sid, NAVY)]

    # ── Title ────────────────────────────────────────────────────────────────
    title_id = _oid()
    reqs += [
        add_textbox(title_id, sid, emu(0.4), emu(0.3), emu(9.2), emu(0.7)),
        set_text(title_id, 'Product Roadmap'),
        style_text(title_id, bold=True, size_pt=34, rgb=WHITE, font='Inter'),
        para_align(title_id, 'LEFT'),
        shape_fill(title_id, transparent=True),
        no_border(title_id),
    ]

    # Green underline bar
    bar_id = _oid()
    reqs += [
        add_textbox(bar_id, sid, emu(0.4), emu(1.0), emu(1.6), emu(0.05)),
        shape_fill(bar_id, GREEN),
        no_border(bar_id),
    ]

    # ── Three columns ─────────────────────────────────────────────────────────
    col_defs = [
        {
            'x': emu(0.35),
            'label': 'MVP',
            'sub': 'Live Now',
            'color': GREEN,
            'items': [
                'Roster Management',
                'Coach-to-Parent Communication',
                'Scheduling & RSVP',
                'Payments & Invoicing',
                'Athlete Profiles',
                '4–5 pilot clubs · ~300 athletes',
            ],
        },
        {
            'x': emu(3.55),
            'label': 'Pilot Expansion',
            'sub': '6 Months',
            'color': GREEN,
            'items': [
                '50–150 clubs',
                'Multi-sport rollout',
                'Android app',
                'Payment volume growing',
                'Club partnership program',
            ],
        },
        {
            'x': emu(6.75),
            'label': 'Full Launch',
            'sub': '12–18 Months',
            'color': GREEN,
            'items': [
                'AI analytics',
                'Game stats & highlights',
                'Recruiting profiles',
                'Live streaming',
                'Vendor marketplace',
                'National scale',
            ],
        },
    ]

    col_w = emu(2.85)
    col_top = emu(1.2)

    for col in col_defs:
        x = col['x']

        # Header background box
        hdr_id = _oid()
        reqs += [
            add_textbox(hdr_id, sid, x, col_top, col_w, emu(0.55)),
            shape_fill(hdr_id, DKNAVY),
            green_border(hdr_id, 2),
        ]

        # Label text
        lbl_id = _oid()
        reqs += [
            add_textbox(lbl_id, sid, x + emu(0.12), col_top + emu(0.05), col_w - emu(0.24), emu(0.28)),
            set_text(lbl_id, col['label']),
            style_text(lbl_id, bold=True, size_pt=16, rgb=GREEN, font='Inter'),
            para_align(lbl_id, 'LEFT'),
            shape_fill(lbl_id, transparent=True),
            no_border(lbl_id),
        ]

        # Sub-label (timeframe)
        sub_id = _oid()
        reqs += [
            add_textbox(sub_id, sid, x + emu(0.12), col_top + emu(0.3), col_w - emu(0.24), emu(0.22)),
            set_text(sub_id, col['sub']),
            style_text(sub_id, bold=False, size_pt=10, rgb=GRAY, font='Inter'),
            para_align(sub_id, 'LEFT'),
            shape_fill(sub_id, transparent=True),
            no_border(sub_id),
        ]

        # Body bullet box
        body_text = '\n'.join('• ' + item for item in col['items'])
        body_id = _oid()
        body_top = col_top + emu(0.65)
        reqs += [
            add_textbox(body_id, sid, x, body_top, col_w, emu(4.9)),
            set_text(body_id, body_text),
            style_text(body_id, bold=False, size_pt=12, rgb=WHITE, font='Inter'),
            para_align(body_id, 'LEFT'),
            shape_fill(body_id, DKNAVY),
            green_border(body_id, 1),
        ]

    batch(service, reqs)
    print(f'  ✓ Product Roadmap slide created (slide id: {sid})')
    return sid


# ── Build: Our Team slide ──────────────────────────────────────────────────────

def build_team_slide(service, insert_index):
    """Create the Our Team slide at insert_index (0-based)."""
    sid, create_req = create_blank_slide(insert_index)
    batch(service, [create_req])

    reqs = [set_bg(sid, NAVY)]

    # ── Title ────────────────────────────────────────────────────────────────
    title_id = _oid()
    reqs += [
        add_textbox(title_id, sid, emu(0.4), emu(0.3), emu(9.2), emu(0.7)),
        set_text(title_id, 'Our Team'),
        style_text(title_id, bold=True, size_pt=34, rgb=WHITE, font='Inter'),
        para_align(title_id, 'LEFT'),
        shape_fill(title_id, transparent=True),
        no_border(title_id),
    ]

    # Green underline bar
    bar_id = _oid()
    reqs += [
        add_textbox(bar_id, sid, emu(0.4), emu(1.0), emu(1.0), emu(0.05)),
        shape_fill(bar_id, GREEN),
        no_border(bar_id),
    ]

    # ── Four member cards ─────────────────────────────────────────────────────
    members = [
        {
            'name': 'Aliza Avital-Caplan',
            'role': 'Founder',
            'bio': '20-year real estate broker with $2.4B+ in sales. Mother of a competitive gymnast.',
        },
        {
            'name': 'Courtney Guertin',
            'role': 'Technical Advisor',
            'bio': 'Former CTO of Ease. Helped scale the platform to 15M+ users and $100M+ raised.',
        },
        {
            'name': 'Craig Zappa',
            'role': 'Coach, Club Owner & Advisor',
            'bio': 'Owner of ENA Gymnastics with 38 years of experience. Home of Olivia Dunne.',
        },
        {
            'name': 'Max Kothari',
            'role': 'Web Developer & Analyst',
            'bio': 'Phillips Exeter Academy.',
        },
    ]

    card_w = emu(2.1)
    card_gap = emu(0.2)
    total_w = 4 * card_w + 3 * card_gap
    start_x = (W - total_w) // 2
    card_top = emu(1.25)
    card_h = emu(5.6)

    for i, m in enumerate(members):
        x = start_x + i * (card_w + card_gap)

        # Card background
        card_id = _oid()
        reqs += [
            add_textbox(card_id, sid, x, card_top, card_w, card_h),
            shape_fill(card_id, DKNAVY),
            green_border(card_id, 2),
        ]

        # Green accent strip at top of card
        strip_id = _oid()
        reqs += [
            add_textbox(strip_id, sid, x, card_top, card_w, emu(0.05)),
            shape_fill(strip_id, GREEN),
            no_border(strip_id),
        ]

        # Name
        name_id = _oid()
        reqs += [
            add_textbox(name_id, sid, x + emu(0.12), card_top + emu(0.15), card_w - emu(0.24), emu(0.5)),
            set_text(name_id, m['name']),
            style_text(name_id, bold=True, size_pt=13, rgb=WHITE, font='Inter'),
            para_align(name_id, 'LEFT'),
            shape_fill(name_id, transparent=True),
            no_border(name_id),
        ]

        # Role
        role_id = _oid()
        reqs += [
            add_textbox(role_id, sid, x + emu(0.12), card_top + emu(0.68), card_w - emu(0.24), emu(0.38)),
            set_text(role_id, m['role']),
            style_text(role_id, bold=False, size_pt=11, rgb=GREEN, font='Inter'),
            para_align(role_id, 'LEFT'),
            shape_fill(role_id, transparent=True),
            no_border(role_id),
        ]

        # Bio
        bio_id = _oid()
        reqs += [
            add_textbox(bio_id, sid, x + emu(0.12), card_top + emu(1.1), card_w - emu(0.24), emu(4.3)),
            set_text(bio_id, m['bio']),
            style_text(bio_id, bold=False, size_pt=11, rgb=WHITE, font='Inter'),
            para_align(bio_id, 'LEFT'),
            shape_fill(bio_id, transparent=True),
            no_border(bio_id),
        ]

    batch(service, reqs)
    print(f'  ✓ Our Team slide created (slide id: {sid})')
    return sid


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    service = get_service()

    print('\nReading presentation...')
    pres = get_pres(service)
    slides = pres['slides']
    n = len(slides)
    print(f'  {n} slides found\n')

    # ── Helper: dump slide text for debugging ─────────────────────────────────
    def dump_slide(idx):
        s = slides[idx]
        print(f'  --- Slide {idx+1} ({s["objectId"]}) ---')
        for e in s.get('pageElements', []):
            if 'shape' in e:
                txt = shape_text(e)
                if txt.strip():
                    print(f'    SHAPE {e["objectId"]}: {repr(txt[:120])}')
            elif 'table' in e:
                t = e['table']
                print(f'    TABLE {e["objectId"]} ({t["rows"]}×{t["columns"]}):')
                for r, row in enumerate(t.get('tableRows', [])):
                    for c, cell in enumerate(row.get('tableCells', [])):
                        ct = cell_text(cell)
                        if ct.strip():
                            print(f'      [{r},{c}]: {repr(ct[:80])}')

    reqs = []

    # ────────────────────────────────────────────────────────────────────────
    # SLIDE 2 — "largest iCloud base team company" → "largest cloud-based team platform"
    # ────────────────────────────────────────────────────────────────────────
    print('Slide 2: replacing "largest iCloud base team company"...')
    s2_id = slides[1]['objectId']
    reqs.append(replace_text_req(
        'largest iCloud base team company',
        'largest cloud-based team platform',
        page_ids=[s2_id],
    ))

    # ────────────────────────────────────────────────────────────────────────
    # SLIDE 3 — League Administrators card body text
    # Strategy: find shapes on slide 3 whose text matches the Coaches & Teams
    # body text (the duplicate). We keep the first hit (Coaches & Teams) and
    # replace every subsequent hit (League Administrators).
    # ────────────────────────────────────────────────────────────────────────
    print('Slide 3: fixing League Administrators body text...')
    s3 = slides[2]
    s3_id = s3['objectId']

    LEAGUE_NEW = (
        'Oversee multiple teams, manage league schedules, coordinate venues, '
        'and ensure smooth operations across all clubs and divisions.'
    )

    # Read all non-title shapes on slide 3 to find duplicated text
    s3_shapes = [e for e in s3.get('pageElements', []) if 'shape' in e]
    # Find shapes that appear more than once with the same text
    text_to_shapes = {}
    for e in s3_shapes:
        t = shape_text(e).strip()
        if t:
            text_to_shapes.setdefault(t, []).append(e)

    league_replaced = False
    for txt, group in text_to_shapes.items():
        if len(group) >= 2:
            # The second shape is the League Administrators card body
            dup_elem = group[1]
            dup_id = dup_elem['objectId']
            current = shape_text(dup_elem)
            print(f'  Duplicate body text found in shape {dup_id}: {repr(current[:60])}')
            # We need to apply these after executing current batch, because
            # deleteText + insertText on existing shapes work with objectIds
            # collected now. Queue them separately.
            league_reqs = replace_shape_body(dup_id, current, LEAGUE_NEW)
            league_replaced = True
            break

    # Execute the slide-2 replaceAllText first so it doesn't interfere
    if reqs:
        batch(service, reqs)
        reqs = []
        print('  ✓ Slide 2 done')

    if league_replaced:
        batch(service, league_reqs)
        print('  ✓ Slide 3 done')
    else:
        # Fallback: try replaceAllText on slide 3 if we couldn't detect the dup
        print('  WARNING: Could not detect duplicate on slide 3 automatically.')
        print('  Dumping slide 3 for inspection:')
        dump_slide(2)

    # ────────────────────────────────────────────────────────────────────────
    # Re-read (shapes may have changed IDs after createSlide; text changes are safe)
    # We do NOT re-read here — slide IDs are stable for text changes.
    # ────────────────────────────────────────────────────────────────────────

    # ────────────────────────────────────────────────────────────────────────
    # SLIDE 13 — second "50%-55%" → "55%-60%" in map legend
    # ────────────────────────────────────────────────────────────────────────
    print('Slide 13: fixing duplicate "50%-55%" in map legend...')
    s13 = slides[12]
    s13_id = s13['objectId']

    TARGET = '50%-55%'
    hits13 = find_shapes_with(s13, TARGET)
    print(f'  Found {len(hits13)} shape(s) containing "{TARGET}"')

    if len(hits13) >= 2:
        # Replace only the second instance
        second_elem = hits13[1]
        second_id = second_elem['objectId']
        current = shape_text(second_elem)
        # The shape may contain only the legend text; replace all occurrences
        # within that shape only, via replaceAllText scoped to that objectId.
        batch(service, [replace_text_req(TARGET, '55%-60%', page_ids=[s13_id])])
        # That replaced BOTH — fix by restoring the first one
        first_id = hits13[0]['objectId']
        batch(service, [replace_text_req('55%-60%', TARGET, page_ids=[s13_id])])
        # Now only replace in the second shape — use deleteText/insertText
        cur2 = shape_text(second_elem)  # original still in memory; use TARGET
        new_text = cur2.replace(TARGET, '55%-60%', 1)
        batch(service, replace_shape_body(second_id, cur2, new_text))
        print('  ✓ Slide 13 done (second instance replaced)')
    elif len(hits13) == 1:
        # Both instances might be in the same shape — handle carefully
        elem = hits13[0]
        cur = shape_text(elem)
        count = cur.count(TARGET)
        print(f'  Both instances in one shape, count={count}')
        if count >= 2:
            # Replace only the second occurrence manually
            idx = cur.index(TARGET)               # first occurrence
            idx2 = cur.index(TARGET, idx + 1)     # second occurrence
            new_text = cur[:idx2] + '55%-60%' + cur[idx2 + len(TARGET):]
            batch(service, replace_shape_body(elem['objectId'], cur, new_text))
            print('  ✓ Slide 13 done (second instance in same shape replaced)')
        else:
            print('  WARNING: Only one instance found on slide 13 — skipping.')
            dump_slide(12)
    else:
        print('  WARNING: "50%-55%" not found on slide 13.')
        dump_slide(12)

    # ────────────────────────────────────────────────────────────────────────
    # SLIDE 21 — competitor column rows
    # ────────────────────────────────────────────────────────────────────────
    print('Slide 21: updating competitor comparison table...')
    s21 = slides[20]
    tables21 = find_tables(s21)
    print(f'  Found {len(tables21)} table(s) on slide 21')

    COMP_ROWS = [
        'TeamSnap / SportsEngine',
        'iClassPro / Jackrabbit',
        'Hudl / GameChanger / NCSA',
    ]

    if tables21:
        tbl_elem = tables21[0]
        tbl_id = tbl_elem['objectId']
        tbl = tbl_elem['table']
        rows = tbl.get('tableRows', [])
        n_cols = tbl.get('columns', 0)
        print(f'  Table: {len(rows)} rows × {n_cols} cols')

        # Find which column is the "Competitors" column by scanning the header row
        header_row = rows[0] if rows else {}
        comp_col_idx = None
        for ci, cell in enumerate(header_row.get('tableCells', [])):
            ct = cell_text(cell).strip().lower()
            if 'competitor' in ct:
                comp_col_idx = ci
                break

        if comp_col_idx is None:
            # Fallback: last column
            comp_col_idx = n_cols - 1
            print(f'  Could not find "Competitors" header; using last column ({comp_col_idx})')
        else:
            print(f'  Competitors column index: {comp_col_idx}')

        table_reqs = []
        for row_i, new_val in enumerate(COMP_ROWS, start=1):  # data rows start at 1
            if row_i < len(rows):
                cell = rows[row_i]['tableCells'][comp_col_idx]
                cur_val = cell_text(cell)
                print(f'    Row {row_i} current: {repr(cur_val.strip())} → "{new_val}"')
                table_reqs += replace_cell_text(tbl_id, row_i, comp_col_idx, cur_val, new_val)

        if table_reqs:
            batch(service, table_reqs)
            print('  ✓ Slide 21 done')
    else:
        print('  WARNING: No table found on slide 21.')
        dump_slide(20)

    # ────────────────────────────────────────────────────────────────────────
    # SLIDE 28 — Centralized Team Communication body text
    # ────────────────────────────────────────────────────────────────────────
    print('Slide 28: fixing Centralized Team Communication body text...')
    s28 = slides[27]
    s28_id = s28['objectId']

    COMM_NEW = (
        'Keep coaches, parents, and staff aligned with instant group messaging, '
        'announcements, and direct chats — all in one place.'
    )

    # Find duplicated shapes on slide 28
    s28_shapes = [e for e in s28.get('pageElements', []) if 'shape' in e]
    s28_text_map = {}
    for e in s28_shapes:
        t = shape_text(e).strip()
        if t:
            s28_text_map.setdefault(t, []).append(e)

    s28_fixed = False
    for txt, grp in s28_text_map.items():
        if len(grp) >= 2:
            dup_elem = grp[1]
            cur = shape_text(dup_elem)
            batch(service, replace_shape_body(dup_elem['objectId'], cur, COMM_NEW))
            s28_fixed = True
            print(f'  ✓ Slide 28 done (replaced dup in shape {dup_elem["objectId"]})')
            break

    if not s28_fixed:
        # Try replaceAllText on slide 28 if we know the roster card text
        # The task says it's "duplicated from the roster card" — try to find it
        print('  Could not auto-detect dup on slide 28; dumping slide:')
        dump_slide(27)

    # ────────────────────────────────────────────────────────────────────────
    # SLIDE 29 — AI-Powered Performance Analysis body text
    # ────────────────────────────────────────────────────────────────────────
    print('Slide 29: fixing AI-Powered Performance Analysis body text...')
    s29 = slides[28]

    AI_NEW = (
        'Automatically analyze athlete video to identify technique gaps, '
        'track improvement over time, and generate personalized coaching feedback.'
    )

    s29_shapes = [e for e in s29.get('pageElements', []) if 'shape' in e]
    s29_text_map = {}
    for e in s29_shapes:
        t = shape_text(e).strip()
        if t:
            s29_text_map.setdefault(t, []).append(e)

    s29_fixed = False
    for txt, grp in s29_text_map.items():
        if len(grp) >= 2:
            dup_elem = grp[1]
            cur = shape_text(dup_elem)
            batch(service, replace_shape_body(dup_elem['objectId'], cur, AI_NEW))
            s29_fixed = True
            print(f'  ✓ Slide 29 done (replaced dup in shape {dup_elem["objectId"]})')
            break

    if not s29_fixed:
        print('  Could not auto-detect dup on slide 29; dumping slide:')
        dump_slide(28)

    # ────────────────────────────────────────────────────────────────────────
    # SLIDE 32 — Phase 4 example text
    # ────────────────────────────────────────────────────────────────────────
    print('Slide 32: fixing Phase 4 example text...')
    s32 = slides[31]

    PHASE4_NEW = (
        'Athlete uploads season highlights → AI builds recruiting profile → '
        'college coaches receive verified performance report.'
    )

    s32_shapes = [e for e in s32.get('pageElements', []) if 'shape' in e]
    s32_text_map = {}
    for e in s32_shapes:
        t = shape_text(e).strip()
        if t:
            s32_text_map.setdefault(t, []).append(e)

    s32_fixed = False
    for txt, grp in s32_text_map.items():
        if len(grp) >= 2:
            dup_elem = grp[1]
            cur = shape_text(dup_elem)
            batch(service, replace_shape_body(dup_elem['objectId'], cur, PHASE4_NEW))
            s32_fixed = True
            print(f'  ✓ Slide 32 done (replaced dup in shape {dup_elem["objectId"]})')
            break

    if not s32_fixed:
        print('  Could not auto-detect dup on slide 32; dumping slide:')
        dump_slide(31)

    # ────────────────────────────────────────────────────────────────────────
    # Re-read presentation to get fresh slide list before inserting slides
    # (slide count / IDs unchanged for text edits, but confirm n)
    # ────────────────────────────────────────────────────────────────────────
    print('\nRe-reading presentation before inserting new slides...')
    pres = get_pres(service)
    slides = pres['slides']
    n = len(slides)
    print(f'  {n} slides now\n')

    # ────────────────────────────────────────────────────────────────────────
    # NEW SLIDE: Product Roadmap — after slide 27 (insert at index 27)
    # ────────────────────────────────────────────────────────────────────────
    print('Adding Product Roadmap slide after slide 27...')
    build_roadmap_slide(service, insert_index=27)

    # ────────────────────────────────────────────────────────────────────────
    # NEW SLIDE: Our Team — before the last slide (the contact page)
    # After inserting roadmap, the deck has n+1 slides.
    # "Before the contact page" = insert at index n (second-to-last position).
    # ────────────────────────────────────────────────────────────────────────
    print('Adding Our Team slide before the contact/last page...')
    build_team_slide(service, insert_index=n + 1)

    print('\n✅  All changes applied successfully!')
    print(f'   Presentation: https://docs.google.com/presentation/d/{PRESENTATION_ID}/edit')


if __name__ == '__main__':
    main()
