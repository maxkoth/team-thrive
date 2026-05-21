#!/usr/bin/env python3
"""
Apply ALL changes to the new TeamThrive presentation.

New presentation ID: 1nZ1YfTqSUfzsBbzZC8azxza9XoPZ66mfJI2fXHOwIIo

Changes:
  Text fixes (slides 3, 13, 19, 20, 21, 28, 29, 32, 33)
  Wes feedback (slides 3, 13, 19, 20, 21)
  New slides: Product Roadmap (after Slide 27) + Our Team (before LET'S CONNECT)
  NO image changes.
"""

import os, sys, uuid, httplib2, google_auth_httplib2
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as SA

NEW_PRES_ID = '1nZ1YfTqSUfzsBbzZC8azxza9XoPZ66mfJI2fXHOwIIo'
SCOPES = ['https://www.googleapis.com/auth/presentations']

# ── Colours ───────────────────────────────────────────────────────────────────
def rgb(h):
    h = h.lstrip('#')
    return {'red': int(h[0:2],16)/255, 'green': int(h[2:4],16)/255, 'blue': int(h[4:6],16)/255}

NAVY   = rgb('0D1B3E'); GREEN  = rgb('3DDC84'); WHITE  = {'red':1.0,'green':1.0,'blue':1.0}
GRAY   = rgb('8892A4'); DKNAVY = rgb('08122A'); MDNAVY = rgb('0F2347')
BLUGRY = rgb('B0BCCC'); BORD   = rgb('1C3060')

# ── Units ─────────────────────────────────────────────────────────────────────
def emu(inches): return int(inches * 914_400)
def pt(p):       return int(p * 12_700)
def _v(v):       return {'magnitude': v, 'unit': 'EMU'}

BASE = 3_000_000
W    = 12_192_000   # 13.3333" widescreen
H    =  6_858_000   # 7.5"

# ── Auth ──────────────────────────────────────────────────────────────────────
def get_service():
    ca  = os.environ.get('REQUESTS_CA_BUNDLE', '/etc/ssl/certs/ca-certificates.crt')
    key = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')
    if not os.path.exists(key): sys.exit(f'Key not found: {key}')
    creds = SA.from_service_account_file(key, scopes=SCOPES)
    return build('slides', 'v1', http=google_auth_httplib2.AuthorizedHttp(creds, http=httplib2.Http(ca_certs=ca)))

def batch(svc, reqs):
    if not reqs: return
    return svc.presentations().batchUpdate(presentationId=NEW_PRES_ID, body={'requests': reqs}).execute()

def _oid(): return 'n_' + uuid.uuid4().hex[:16]

# ── Text extraction ───────────────────────────────────────────────────────────
def shape_text(elem):
    parts = []
    for te in elem.get('shape', {}).get('text', {}).get('textElements', []):
        if 'textRun' in te: parts.append(te['textRun'].get('content', ''))
    return ''.join(parts)

def cell_text(cell):
    parts = []
    for te in cell.get('text', {}).get('textElements', []):
        if 'textRun' in te: parts.append(te['textRun'].get('content', ''))
    return ''.join(parts)

def _search(elements, oid):
    for e in elements:
        if e['objectId'] == oid and 'shape' in e: return shape_text(e)
        if 'elementGroup' in e:
            r = _search(e['elementGroup'].get('children', []), oid)
            if r is not None: return r
    return None

def get_txt(slides, oid):
    for s in slides:
        r = _search(s.get('pageElements', []), oid)
        if r is not None: return r
    return None

def get_cell(slides, tbl_oid, row, col):
    for s in slides:
        for e in s.get('pageElements', []):
            if e['objectId'] == tbl_oid and 'table' in e:
                rows = e['table'].get('tableRows', [])
                if row < len(rows):
                    cells = rows[row].get('tableCells', [])
                    if col < len(cells): return cell_text(cells[col])
    return None

# ── Request builders ──────────────────────────────────────────────────────────
def del_txt(oid, start, end, cell=None):
    r = {'objectId': oid, 'textRange': {'type': 'FIXED_RANGE', 'startIndex': start, 'endIndex': end}}
    if cell: r['cellLocation'] = cell
    return {'deleteText': r}

def ins_txt(oid, text, idx=0, cell=None):
    r = {'objectId': oid, 'text': text, 'insertionIndex': idx}
    if cell: r['cellLocation'] = cell
    return {'insertText': r}

def replace_shape(oid, current, new):
    reqs = []
    if len(current) > 0:
        reqs.append(del_txt(oid, 0, len(current)))
    reqs.append(ins_txt(oid, new))
    return reqs

def replace_cell(tbl_oid, row, col, current, new):
    loc = {'rowIndex': row, 'columnIndex': col}
    reqs = []
    # The trailing \n in a table cell is protected and cannot be deleted
    deletable = current.rstrip('\n')
    if len(deletable) > 0:
        reqs.append(del_txt(tbl_oid, 0, len(deletable), cell=loc))
    reqs.append(ins_txt(tbl_oid, new, cell=loc))
    return reqs

# ── Shape factory (createShape uses scaleX/scaleY for actual size) ─────────────
def _mk(oid, sid, stype, tx, ty, sx, sy):
    return {'createShape': {'objectId': oid, 'shapeType': stype,
        'elementProperties': {'pageObjectId': sid,
            'size': {'width': _v(BASE), 'height': _v(BASE)},
            'transform': {'scaleX': sx, 'scaleY': sy,
                          'translateX': int(tx), 'translateY': int(ty), 'unit': 'EMU'}}}}

def box(oid, sid, x, y, w, h):
    return _mk(oid, sid, 'TEXT_BOX', emu(x), emu(y), emu(w)/BASE, emu(h)/BASE)
def rct(oid, sid, x, y, w, h):
    return _mk(oid, sid, 'RECTANGLE', emu(x), emu(y), emu(w)/BASE, emu(h)/BASE)

# ── Style helpers ─────────────────────────────────────────────────────────────
def txt(oid, text): return {'insertText': {'objectId': oid, 'text': text, 'insertionIndex': 0}}
def algn(oid, a='START'): return {'updateParagraphStyle': {'objectId': oid,
    'style': {'alignment': a}, 'textRange': {'type': 'ALL'}, 'fields': 'alignment'}}
def sfill(oid, color=None, transparent=False):
    f = {'propertyState': 'NOT_RENDERED'} if transparent else {'solidFill': {'color': {'rgbColor': color}}}
    return {'updateShapeProperties': {'objectId': oid,
        'shapeProperties': {'shapeBackgroundFill': f}, 'fields': 'shapeBackgroundFill'}}
def nborder(oid): return {'updateShapeProperties': {'objectId': oid,
    'shapeProperties': {'outline': {'propertyState': 'NOT_RENDERED'}}, 'fields': 'outline'}}
def sborder(oid, color, w_pt=1.5): return {'updateShapeProperties': {'objectId': oid,
    'shapeProperties': {'outline': {
        'outlineFill': {'solidFill': {'color': {'rgbColor': color}}},
        'weight': _v(pt(w_pt)), 'propertyState': 'RENDERED'}}, 'fields': 'outline'}}
def sbg(sid, color): return {'updatePageProperties': {'objectId': sid,
    'pageProperties': {'pageBackgroundFill': {'solidFill': {'color': {'rgbColor': color}}}},
    'fields': 'pageBackgroundFill'}}
def ctop(oid): return {'updateShapeProperties': {'objectId': oid,
    'shapeProperties': {'contentAlignment': 'TOP'}, 'fields': 'contentAlignment'}}
def tstyle(oid, bold=None, italic=None, size=None, color=None, font=None, s=None, e=None):
    st, flds = {}, []
    if bold  is not None: st['bold']   = bold;  flds.append('bold')
    if size  is not None: st['fontSize'] = _v(pt(size)); flds.append('fontSize')
    if color is not None: st['foregroundColor'] = {'opaqueColor': {'rgbColor': color}}; flds.append('foregroundColor')
    if font  is not None: st['fontFamily'] = font; flds.append('fontFamily')
    tr = {'type': 'ALL'} if s is None else {'type': 'FIXED_RANGE', 'startIndex': s, 'endIndex': e}
    return {'updateTextStyle': {'objectId': oid, 'style': st, 'textRange': tr, 'fields': ','.join(flds)}}


# ══════════════════════════════════════════════════════════════════════════════
# TEXT FIXES
# ══════════════════════════════════════════════════════════════════════════════

def fix_slide3_league_admin(slides):
    """Fix League Administrators body — same text as Coaches & Teams."""
    oid = 'p3_i82'
    t = get_txt(slides, oid)
    if t is None:
        print(f'  [3] p3_i82 not found'); return []
    print(f'  [3] p3_i82: {repr(t[:70])}')

    CORRECT = ('League Administrators\nOversee multiple teams, manage league schedules, '
               'coordinate venues, and ensure smooth operations across all clubs and divisions.')
    if 'Oversee multiple teams' in t:
        print('    -> already correct, skipping')
        return []
    # Replace everything except the trailing \n
    content = t.rstrip('\n')
    new_content = CORRECT
    reqs = [del_txt(oid, 0, len(content)), ins_txt(oid, new_content)]
    print(f'    -> fixing body text')
    return reqs


def fix_slide13_legend(slides):
    """Fix map legend: 45-50%→45%-50%, second 50%-55%→55%-60%."""
    reqs = []

    # Fix p13_i68: '45-50%' → '45%-50%'
    t68 = get_txt(slides, 'p13_i68')
    print(f'  [13a] p13_i68: {repr(t68)}')
    if t68 and t68.startswith('45-50%'):
        reqs += [del_txt('p13_i68', 0, 6), ins_txt('p13_i68', '45%-50%')]
        print(f'    -> fixing to 45%-50%')

    # Fix p13_i74: second '50%-55%' → '55%-60%'
    t74 = get_txt(slides, 'p13_i74')
    print(f'  [13b] p13_i74: {repr(t74)}')
    if t74 and t74.startswith('50%-55%'):
        reqs += [del_txt('p13_i74', 0, 7), ins_txt('p13_i74', '55%-60%')]
        print(f'    -> fixing duplicate to 55%-60%')

    return reqs


def fix_slide19_fee_clarity(slides):
    """Clarify fees apply to competition/travel, not monthly tuition."""
    oid = 'p19_i35'
    t = get_txt(slides, oid)
    print(f'  [19] p19_i35: {repr(t)}')
    OLD = 'APPLIED TO ALL PAYMENTS VIA STRIPE'
    NEW = 'APPLIED TO COMPETITION FEES, TRAVEL & CAMPS — NOT MONTHLY TUITION'
    if t and OLD in t:
        reqs = [del_txt(oid, 0, len(OLD)), ins_txt(oid, NEW)]
        print(f'    -> updating fee description')
        return reqs
    print(f'    -> not found or already updated')
    return []


def fix_slide20_title(slides):
    """Remove '(ON $29.97M ARR)' from gross profit title."""
    oid = 'p20_i4'
    t = get_txt(slides, oid)
    print(f'  [20] p20_i4: {repr(t)}')
    OLD = 'GROSS PROFIT SCENARIOS (ON $29.97M ARR)'
    NEW = 'GROSS PROFIT SCENARIOS'
    if t and OLD in t:
        reqs = [del_txt(oid, 0, len(OLD)), ins_txt(oid, NEW)]
        print(f'    -> removing ARR from title')
        return reqs
    print(f'    -> already fixed or not found')
    return []


def fix_slide21_competitor_table(slides):
    """Overhaul competitor table: name real competitors, add NCSA row."""
    tbl_oid = 'p21_i2'
    reqs = []

    # --- Row 1 col 1: replace generic text with TeamSnap / SportsEngine ---
    r1c1 = get_cell(slides, tbl_oid, 1, 1)
    print(f'  [21] row1 col1: {repr(r1c1[:60] if r1c1 else None)}')
    if r1c1 and 'TeamSnap' not in r1c1:
        reqs += replace_cell(tbl_oid, 1, 1, r1c1, 'TeamSnap / SportsEngine')
        print(f'    -> setting to TeamSnap / SportsEngine')

    # --- Row 2 col 1: replace generic text with iClassPro / Jackrabbit ---
    r2c1 = get_cell(slides, tbl_oid, 2, 1)
    print(f'  [21] row2 col1: {repr(r2c1[:60] if r2c1 else None)}')
    if r2c1 and 'iClassPro' not in r2c1:
        reqs += replace_cell(tbl_oid, 2, 1, r2c1, 'iClassPro / Jackrabbit')
        print(f'    -> setting to iClassPro / Jackrabbit')

    # --- Row 3 col 0: rename 'Sport Coverage' → 'Stats & Video' ---
    r3c0 = get_cell(slides, tbl_oid, 3, 0)
    print(f'  [21] row3 col0: {repr(r3c0)}')
    if r3c0 and r3c0.strip() == 'Sport Coverage':
        reqs += replace_cell(tbl_oid, 3, 0, r3c0, 'Stats & Video')
        print(f'    -> renaming to Stats & Video')

    # --- Row 3 col 1: replace generic text with Hudl / GameChanger ---
    r3c1 = get_cell(slides, tbl_oid, 3, 1)
    print(f'  [21] row3 col1: {repr(r3c1[:60] if r3c1 else None)}')
    if r3c1 and 'Hudl' not in r3c1:
        reqs += replace_cell(tbl_oid, 3, 1, r3c1, 'Hudl / GameChanger')
        print(f'    -> setting to Hudl / GameChanger')

    # --- Row 3 col 2: update Team Thrive desc to focus on stats/video ---
    r3c2 = get_cell(slides, tbl_oid, 3, 2)
    print(f'  [21] row3 col2: {repr(r3c2[:60] if r3c2 else None)}')
    STATS_DESC = 'Built-in performance tracking, video sharing, and athlete stats — accessible to coaches, parents, and athletes in real time.'
    if r3c2 and 'tracking, video' not in r3c2:
        reqs += replace_cell(tbl_oid, 3, 2, r3c2, STATS_DESC)
        print(f'    -> updating row 3 col 2 to stats/video description')

    # --- Insert new row 4 for NCSA / SportsRecruits ---
    print(f'  [21] inserting recruiting row...')
    reqs.append({'insertTableRows': {
        'tableObjectId': tbl_oid,
        'cellLocation': {'rowIndex': 3, 'columnIndex': 0},
        'insertBelow': True,
        'number': 1
    }})
    new_cells = [
        (4, 0, 'Recruiting'),
        (4, 1, 'NCSA / SportsRecruits'),
        (4, 2, 'Verified athlete profiles, coach-facing highlight reels, and recruiting tools built directly into the platform.'),
    ]
    for ri, ci, text in new_cells:
        reqs.append(ins_txt(tbl_oid, text, cell={'rowIndex': ri, 'columnIndex': ci}))
    print(f'    -> added row 4: NCSA/SportsRecruits')

    return reqs


def fix_slide28_team_comm(slides):
    """Fix slide 28 Team Communication body (same as Roster Management)."""
    oid = 'p28_i48'
    t = get_txt(slides, oid)
    print(f'  [28] p28_i48: {repr(t[:80] if t else None)}')
    COMM_TITLE = 'CENTRALIZED TEAM COMMUNICATION\n'
    COMM_NEW = (COMM_TITLE + 'Keep coaches, parents, and staff aligned with instant group '
                'messaging, announcements, and direct chats — all in one place.')
    if t and 'aligned with instant group' in t:
        print(f'    -> already fixed')
        return []
    if t and t.startswith(COMM_TITLE):
        body_start = len(COMM_TITLE)
        body = t[body_start:].rstrip('\n')
        if body:
            reqs = [del_txt(oid, body_start, body_start + len(body)),
                    ins_txt(oid, 'Keep coaches, parents, and staff aligned with instant group messaging, announcements, and direct chats — all in one place.', body_start)]
            print(f'    -> fixing team comm body')
            return reqs
    if t and 'CENTRALIZED' in t:
        # Replace everything
        content = t.rstrip('\n')
        reqs = replace_shape(oid, content, COMM_NEW)
        print(f'    -> replacing full team comm text')
        return reqs
    print(f'    -> shape not found or unexpected format')
    return []


def fix_slide29_ai_analysis(slides):
    """Fix slide 29 AI-Powered Performance Analysis body (same as Drills)."""
    oid = 'p29_i16'
    t = get_txt(slides, oid)
    print(f'  [29] p29_i16: {repr(t[:80] if t else None)}')
    AI_TITLE = 'AI-POWERED PERFORMANCE ANALYSIS\n'
    AI_NEW_BODY = ('Automatically analyze athlete video to identify technique gaps, '
                   'track improvement over time, and generate personalized coaching feedback.')
    if t and 'identify technique gaps' in t:
        print(f'    -> already fixed')
        return []
    if t and t.startswith(AI_TITLE):
        body_start = len(AI_TITLE)
        body = t[body_start:].rstrip('\n')
        if body:
            reqs = [del_txt(oid, body_start, body_start + len(body)),
                    ins_txt(oid, AI_NEW_BODY, body_start)]
            print(f'    -> fixing AI analysis body')
            return reqs
    if t and 'AI-POWERED' in t:
        content = t.rstrip('\n')
        reqs = replace_shape(oid, content, AI_TITLE + AI_NEW_BODY)
        print(f'    -> replacing full AI analysis text')
        return reqs
    print(f'    -> shape not found or unexpected format')
    return []


def fix_slide32_phase4(slides):
    """Fix slide 32 Phase 4 example text (duplicate of Phase 3)."""
    oid = 'p32_i34'
    t = get_txt(slides, oid)
    print(f'  [32] p32_i34: {repr(t[:80] if t else None)}')
    PHASE4_NEW = ('Example\n\nAthlete uploads season highlights → AI builds recruiting profile → '
                  'college coaches receive verified performance report.')
    if t and 'recruiting profile' in t:
        print(f'    -> already fixed')
        return []
    if t and 'Example' in t:
        content = t.rstrip('\n')
        reqs = replace_shape(oid, content, PHASE4_NEW)
        print(f'    -> fixing Phase 4 example text')
        return reqs
    print(f'    -> shape not found')
    return []


def fix_slide33_courtney_ronas(slides):
    """Update Courtney Guertin's advisor slide to mention Ronas dev team."""
    oid = 'p33_i13'
    t = get_txt(slides, oid)
    print(f'  [33] p33_i13: {repr(t[:100] if t else None)}')
    if t is None:
        print(f'    -> not found')
        return []
    if 'Ronas' in t:
        print(f'    -> already mentions Ronas')
        return []

    # Add Ronas sentence after the existing description
    # Find the end of the text body (before trailing \n)
    content = t.rstrip('\n')
    RONAS_SUFFIX = ' Overseeing development with Ronas, a European mobile dev team building the platform from the ground up.'
    new_content = content + RONAS_SUFFIX
    reqs = replace_shape(oid, content, new_content)
    print(f'    -> adding Ronas mention')
    return reqs


# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT ROADMAP SLIDE
# ══════════════════════════════════════════════════════════════════════════════

def build_roadmap(svc, sid):
    reqs = [sbg(sid, NAVY)]

    tid = _oid()
    reqs += [box(tid, sid, 0.55, 0.28, 12.23, 0.72), txt(tid, 'Product Roadmap'),
             tstyle(tid, bold=True, size=36, color=WHITE, font='Inter'),
             algn(tid, 'START'), sfill(tid, transparent=True), nborder(tid)]

    bid = _oid()
    reqs += [rct(bid, sid, 0.55, 1.07, 1.5, 0.055), sfill(bid, GREEN), nborder(bid)]

    margin = 0.55; gap = 0.28
    col_w  = (13.333 - 2*margin - 2*gap) / 3
    col_xs = [margin, margin + col_w + gap, margin + 2*(col_w + gap)]
    c_top  = 1.22; hdr_h = 0.80; gapv = 0.06
    body_h = H/914_400 - c_top - hdr_h - gapv - 0.28

    phases = [
        {'label': 'MVP', 'sub': 'Live Now',
         'items': ['Roster & Athlete Profiles', 'Coach-to-Parent Messaging',
                   'Scheduling & RSVP', 'Payments & Invoicing',
                   '4–5 pilot clubs · ~300 athletes']},
        {'label': 'Pilot Expansion', 'sub': '6 Months',
         'items': ['50–150 clubs onboarded', 'Multi-sport rollout',
                   'Android app launch', 'Growing payment volume',
                   'Club partnership program']},
        {'label': 'Full Launch', 'sub': '12–18 Months',
         'items': ['AI performance analytics', 'Game stats & highlights',
                   'Athlete recruiting profiles', 'Live streaming integration',
                   'Vendor marketplace · National scale']},
    ]

    for i, ph in enumerate(phases):
        x = col_xs[i]
        hid = _oid()
        reqs += [rct(hid, sid, x, c_top, col_w, hdr_h), sfill(hid, DKNAVY), sborder(hid, GREEN, 1.5)]

        label, sub = ph['label'], ph['sub']
        merged = f'{label}\n{sub}'
        ll, tl = len(label), len(merged)
        htid = _oid()
        reqs += [box(htid, sid, x+0.18, c_top+0.10, col_w-0.36, hdr_h-0.20),
                 txt(htid, merged),
                 tstyle(htid, bold=True,  size=18, color=GREEN, font='Inter', s=0,    e=ll),
                 tstyle(htid, bold=False, size=10, color=GRAY,  font='Inter', s=ll+1, e=tl),
                 algn(htid, 'START'), sfill(htid, transparent=True), nborder(htid)]

        by = c_top + hdr_h + gapv
        bkid = _oid()
        reqs += [rct(bkid, sid, x, by, col_w, body_h), sfill(bkid, MDNAVY), sborder(bkid, BORD, 1)]

        btid = _oid()
        body_txt = '\n'.join(f'  ●  {it}' for it in ph['items'])
        reqs += [box(btid, sid, x+0.20, by+0.22, col_w-0.40, body_h-0.44),
                 txt(btid, body_txt),
                 tstyle(btid, bold=False, size=14, color=WHITE, font='Inter'),
                 algn(btid, 'START'), sfill(btid, transparent=True), nborder(btid), ctop(btid)]

    batch(svc, reqs)
    print(f'  ✓ Product Roadmap built on slide {sid}')


# ══════════════════════════════════════════════════════════════════════════════
# OUR TEAM SLIDE
# ══════════════════════════════════════════════════════════════════════════════

def build_team(svc, sid):
    reqs = [sbg(sid, NAVY)]

    tid = _oid()
    reqs += [box(tid, sid, 0.55, 0.28, 12.23, 0.72), txt(tid, 'Our Team'),
             tstyle(tid, bold=True, size=36, color=WHITE, font='Inter'),
             algn(tid, 'START'), sfill(tid, transparent=True), nborder(tid)]

    bid = _oid()
    reqs += [rct(bid, sid, 0.55, 1.07, 1.0, 0.055), sfill(bid, GREEN), nborder(bid)]

    members = [
        {'name': 'Aliza Avital-Caplan', 'role': 'Founder',
         'bio': '20-year real estate broker with $2.4B+ in sales. Mother of a competitive gymnast '
                '— built TeamThrive to solve the scheduling and communication chaos she lived every season.'},
        {'name': 'Courtney Guertin', 'role': 'Technical Advisor',
         'bio': 'Former CTO of Ease, scaled to 15M+ users and $100M+ raised. Overseeing development '
                'with Ronas, a European mobile dev team building the platform from the ground up.'},
        {'name': 'Craig Zappa', 'role': 'Coach, Club Owner & Advisor',
         'bio': 'Owner of ENA Gymnastics with 38 years of coaching experience. '
                'Home to Olympian Olivia Dunne. Deep operator insight into what elite club programs need.'},
        {'name': 'Max Kothari', 'role': 'Web Developer & Analyst',
         'bio': 'Phillips Exeter Academy. Brings sharp analytical and full-stack technical skills to the team.'},
    ]

    margin = 0.55; gap_x = 0.28
    card_w = (13.333 - 2*margin - gap_x) / 2
    card_h = 2.72; gap_y = 0.22
    row_ys = [1.3, 1.3 + card_h + gap_y]

    for i, m in enumerate(members):
        row = i // 2; col = i % 2
        x   = margin + col * (card_w + gap_x)
        y   = row_ys[row]
        pad = 0.24; iw = card_w - 2*pad

        cid = _oid()
        reqs += [rct(cid, sid, x, y, card_w, card_h), sfill(cid, DKNAVY), sborder(cid, BORD, 1)]

        stid = _oid()
        reqs += [rct(stid, sid, x, y, card_w, 0.055), sfill(stid, GREEN), nborder(stid)]

        name_y = y + 0.055 + 0.14
        nid    = _oid()
        reqs  += [box(nid, sid, x+pad, name_y, iw, 0.44), txt(nid, m['name']),
                  tstyle(nid, bold=True, size=15, color=WHITE, font='Inter'),
                  algn(nid, 'START'), sfill(nid, transparent=True), nborder(nid)]

        role_y = name_y + 0.44 + 0.06
        rid    = _oid()
        reqs  += [box(rid, sid, x+pad, role_y, iw, 0.38), txt(rid, m['role']),
                  tstyle(rid, bold=False, size=11, color=GREEN, font='Inter'),
                  algn(rid, 'START'), sfill(rid, transparent=True), nborder(rid)]

        div_y = role_y + 0.38 + 0.10
        did   = _oid()
        reqs += [rct(did, sid, x+pad, div_y, iw, 0.012), sfill(did, BORD), nborder(did)]

        bio_y = div_y + 0.012 + 0.10
        bio_h = (y + card_h) - bio_y - 0.12
        bioid = _oid()
        reqs += [box(bioid, sid, x+pad, bio_y, iw, bio_h), txt(bioid, m['bio']),
                 tstyle(bioid, bold=False, size=11, color=BLUGRY, font='Inter'),
                 algn(bioid, 'START'), sfill(bioid, transparent=True), nborder(bioid), ctop(bioid)]

    batch(svc, reqs)
    print(f'  ✓ Our Team built on slide {sid}')


def create_slide(svc, insert_index):
    """Create a blank slide at the given index, return its objectId."""
    sid = _oid()
    batch(svc, [{'createSlide': {
        'objectId': sid,
        'insertionIndex': insert_index,
    }}])
    return sid


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    svc = get_service()
    pres = svc.presentations().get(presentationId=NEW_PRES_ID).execute()
    slides = pres['slides']
    print(f'Loaded: {len(slides)} slides, canvas {pres["pageSize"]["width"]["magnitude"]}×{pres["pageSize"]["height"]["magnitude"]} EMU\n')

    all_reqs = []

    print('--- Text fixes ---')
    all_reqs += fix_slide3_league_admin(slides)
    all_reqs += fix_slide13_legend(slides)
    all_reqs += fix_slide19_fee_clarity(slides)
    all_reqs += fix_slide20_title(slides)
    all_reqs += fix_slide21_competitor_table(slides)
    all_reqs += fix_slide28_team_comm(slides)
    all_reqs += fix_slide29_ai_analysis(slides)
    all_reqs += fix_slide32_phase4(slides)
    all_reqs += fix_slide33_courtney_ronas(slides)

    print(f'\nApplying {len(all_reqs)} text fix requests...')
    batch(svc, all_reqs)
    print('  ✓ Text fixes applied')

    # --- Re-read to confirm new slide count ---
    pres = svc.presentations().get(presentationId=NEW_PRES_ID).execute()
    slides = pres['slides']
    n = len(slides)
    print(f'\n{n} slides after text fixes')

    # Find insertion points by searching slide titles
    early_launch_idx = None
    letsconnect_idx  = None
    for i, s in enumerate(slides):
        for e in s.get('pageElements', []):
            if 'shape' in e:
                t = shape_text(e).strip()
                if 'EARLY LAUNCH TRACTION' in t:
                    early_launch_idx = i
                elif "LET'S CONNECT" in t or "LET’S CONNECT" in t:
                    letsconnect_idx = i

    print(f'  EARLY LAUNCH TRACTION: slide {early_launch_idx+1 if early_launch_idx is not None else "?"}')
    print(f'  LET\'S CONNECT: slide {letsconnect_idx+1 if letsconnect_idx is not None else "?"}')

    # Insert Product Roadmap after EARLY LAUNCH TRACTION
    roadmap_insert = (early_launch_idx + 1) if early_launch_idx is not None else 27
    print(f'\nInserting Product Roadmap at index {roadmap_insert}...')
    roadmap_sid = create_slide(svc, roadmap_insert)
    print(f'  slide id: {roadmap_sid}')
    build_roadmap(svc, roadmap_sid)

    # Re-read to get updated slide list
    pres = svc.presentations().get(presentationId=NEW_PRES_ID).execute()
    slides = pres['slides']
    n = len(slides)
    print(f'\n{n} slides after Product Roadmap')

    # Find LET'S CONNECT again (index shifted by 1 after roadmap insertion)
    letsconnect_idx = None
    for i, s in enumerate(slides):
        for e in s.get('pageElements', []):
            if 'shape' in e:
                t = shape_text(e).strip()
                if "LET'S CONNECT" in t or "LET’S CONNECT" in t or "LET" in t and "CONNECT" in t:
                    letsconnect_idx = i
                    break
        if letsconnect_idx is not None: break

    team_insert = letsconnect_idx if letsconnect_idx is not None else (n - 1)
    print(f'\nInserting Our Team at index {team_insert} (before LET\'S CONNECT)...')
    team_sid = create_slide(svc, team_insert)
    print(f'  slide id: {team_sid}')
    build_team(svc, team_sid)

    pres = svc.presentations().get(presentationId=NEW_PRES_ID).execute()
    print(f'\n✅ Done — {len(pres["slides"])} total slides')
    print(f'   https://docs.google.com/presentation/d/{NEW_PRES_ID}/edit')


if __name__ == '__main__':
    main()
