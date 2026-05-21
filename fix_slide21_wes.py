#!/usr/bin/env python3
"""Fix slide 21 competitor table to fully follow Wes's advice:
1. Rename category labels to match Wes's framing
2. Update Team Thrive column to articulate WHY they win
3. Add Athlete Identity row — the horizontal layer nobody owns
"""

import os, httplib2, google_auth_httplib2
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as SA

PRES = '1nZ1YfTqSUfzsBbzZC8azxza9XoPZ66mfJI2fXHOwIIo'
SCOPES = ['https://www.googleapis.com/auth/presentations']

def get_service():
    creds = SA.from_service_account_file(
        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json'),
        scopes=SCOPES)
    return build('slides', 'v1',
        http=google_auth_httplib2.AuthorizedHttp(creds,
            http=httplib2.Http(ca_certs='/etc/ssl/certs/ca-certificates.crt')))

def batch(svc, reqs):
    if not reqs: return
    return svc.presentations().batchUpdate(
        presentationId=PRES, body={'requests': reqs}).execute()

def cell_text(cell):
    return ''.join(te['textRun']['content']
        for te in cell.get('text',{}).get('textElements',[]) if 'textRun' in te)

def del_cell(tbl, row, col, current):
    deletable = current.rstrip('\n')
    if not deletable: return []
    return [{'deleteText': {
        'objectId': tbl,
        'cellLocation': {'rowIndex': row, 'columnIndex': col},
        'textRange': {'type': 'FIXED_RANGE', 'startIndex': 0, 'endIndex': len(deletable)}
    }}]

def ins_cell(tbl, row, col, text):
    return [{'insertText': {
        'objectId': tbl,
        'cellLocation': {'rowIndex': row, 'columnIndex': col},
        'insertionIndex': 0,
        'text': text
    }}]

def set_cell(tbl, row, col, current, new):
    return del_cell(tbl, row, col, current) + ins_cell(tbl, row, col, new)

def main():
    svc = get_service()
    pres = svc.presentations().get(presentationId=PRES).execute()

    # Find the competitive comparison table (slide 21 = index 20)
    slide = pres['slides'][20]
    tbl_oid = None
    tbl_data = None
    for e in slide.get('pageElements', []):
        if 'table' in e:
            tbl_oid = e['objectId']
            tbl_data = e['table']
            break

    if tbl_oid != 'p21_i2':
        print(f'WARNING: expected p21_i2, got {tbl_oid}')

    rows = tbl_data.get('tableRows', [])
    print(f'Table {tbl_oid}: {len(rows)} rows')
    for r, row in enumerate(rows):
        for c, cell in enumerate(row.get('tableCells', [])):
            ct = cell_text(cell)
            if ct.strip():
                print(f'  [{r},{c}]: {repr(ct[:70])}')

    reqs = []

    # ── Row 1: "Platform Focus" → "Team Management" ───────────────────────────
    r1c0 = cell_text(rows[1]['tableCells'][0])
    print(f'\n[1,0] current: {repr(r1c0)}')
    if 'Team Management' not in r1c0:
        reqs += set_cell(tbl_oid, 1, 0, r1c0, 'Team Management')
        print('  -> renaming to Team Management')

    # Team Thrive col: articulate the win vs TeamSnap/SportsEngine
    r1c2 = cell_text(rows[1]['tableCells'][2])
    NEW_R1C2 = ('Replaces the fragmented app stack — scheduling, communication, '
                'payments, and profiles unified under one login for every role.')
    if NEW_R1C2 not in r1c2:
        reqs += set_cell(tbl_oid, 1, 2, r1c2, NEW_R1C2)
        print('  -> updating TT win vs TeamSnap')

    # ── Row 2: "Features" → "Operations" ─────────────────────────────────────
    r2c0 = cell_text(rows[2]['tableCells'][0])
    print(f'\n[2,0] current: {repr(r2c0)}')
    if 'Operations' not in r2c0:
        reqs += set_cell(tbl_oid, 2, 0, r2c0, 'Operations')
        print('  -> renaming to Operations')

    # Team Thrive col: articulate the win vs iClassPro/Jackrabbit
    r2c2 = cell_text(rows[2]['tableCells'][2])
    NEW_R2C2 = ('Free for clubs, zero migration risk. Captures competition fees, '
                'travel, and camps — the transaction layer iClassPro doesn\'t touch.')
    if NEW_R2C2 not in r2c2:
        reqs += set_cell(tbl_oid, 2, 2, r2c2, NEW_R2C2)
        print('  -> updating TT win vs iClassPro')

    # ── Row 3 col 2: articulate the win vs Hudl/GameChanger ──────────────────
    r3c2 = cell_text(rows[3]['tableCells'][2])
    NEW_R3C2 = ('Sport-agnostic stats and video for ALL sports — not just '
                'football and basketball. Every highlight stays on the athlete\'s permanent record.')
    if NEW_R3C2 not in r3c2:
        reqs += set_cell(tbl_oid, 3, 2, r3c2, NEW_R3C2)
        print('  -> updating TT win vs Hudl')

    # ── Row 4 col 2: articulate the win vs NCSA/SportsRecruits ───────────────
    r4c2 = cell_text(rows[4]['tableCells'][2])
    NEW_R4C2 = ('Recruiting is built in from day one — not a separate paid '
                'platform. Coaches access verified stats and video without leaving the app.')
    if NEW_R4C2 not in r4c2:
        reqs += set_cell(tbl_oid, 4, 2, r4c2, NEW_R4C2)
        print('  -> updating TT win vs NCSA')

    # ── Insert new row 5: Athlete Identity ───────────────────────────────────
    print('\nInserting Athlete Identity row...')
    reqs.append({'insertTableRows': {
        'tableObjectId': tbl_oid,
        'cellLocation': {'rowIndex': 4, 'columnIndex': 0},
        'insertBelow': True,
        'number': 1
    }})
    new_cells = [
        (5, 0, 'Athlete Identity'),
        (5, 1, 'No tool owns this'),
        (5, 2, ('Unified longitudinal record — every stat, video, and milestone '
                'from first practice to college signing, all in one platform. '
                'The layer that makes every other tool more valuable.')),
    ]
    for ri, ci, text in new_cells:
        reqs.append({'insertText': {
            'objectId': tbl_oid,
            'cellLocation': {'rowIndex': ri, 'columnIndex': ci},
            'insertionIndex': 0,
            'text': text
        }})
        print(f'  [{ri},{ci}]: {repr(text[:60])}')

    print(f'\nApplying {len(reqs)} requests...')
    batch(svc, reqs)
    print('✓ Slide 21 updated')

if __name__ == '__main__':
    main()
