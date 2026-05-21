#!/usr/bin/env python3
"""Apply Wes Jones feedback to the TeamThrive Google Slides presentation.

Changes:
  1. Slide 3: Add missing newline in League Administrators card
  2. Slide 13: Fix map legend "45-50%" -> "45%-50%" for consistency
  3. Slide 20: Remove "(ON $29.97M ARR)" from title
  4. Slide 21: Split competitor row — separate NCSA/SportsRecruits from Hudl/GameChanger
  5. Slide 19: Clarify transaction fees apply to competition/travel, not monthly tuition
  6. Our Team: Update Courtney's description to mention Ronas dev team
"""

import os
import sys
import httplib2
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as SACredentials
import google_auth_httplib2

PRESENTATION_ID = '1FNIUCC8jPqpwL8xTrQ33J3vGFwuaULhyp_BknKOuIjk'
SCOPES = ['https://www.googleapis.com/auth/presentations']


def get_service():
    ca_bundle = '/etc/ssl/certs/ca-certificates.crt'
    key_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')
    creds = SACredentials.from_service_account_file(key_path, scopes=SCOPES)
    h = httplib2.Http(ca_certs=ca_bundle)
    return build('slides', 'v1', http=google_auth_httplib2.AuthorizedHttp(creds, http=h))


def batch(service, requests):
    if not requests:
        print('  (no requests to send)')
        return
    resp = service.presentations().batchUpdate(
        presentationId=PRESENTATION_ID,
        body={'requests': requests}
    ).execute()
    print(f'  batchUpdate OK — {len(requests)} request(s)')
    return resp


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


def _search_elements(elements, oid):
    for elem in elements:
        if elem['objectId'] == oid and 'shape' in elem:
            return shape_text(elem)
        if 'elementGroup' in elem:
            result = _search_elements(elem['elementGroup'].get('children', []), oid)
            if result is not None:
                return result
    return None


def get_shape_text_by_id(slides, oid):
    for slide in slides:
        result = _search_elements(slide.get('pageElements', []), oid)
        if result is not None:
            return result
    return None


def get_table_cell_text(slides, table_oid, row, col):
    for slide in slides:
        for elem in slide.get('pageElements', []):
            if elem['objectId'] == table_oid and 'table' in elem:
                rows = elem['table'].get('tableRows', [])
                if row < len(rows):
                    cells = rows[row].get('tableCells', [])
                    if col < len(cells):
                        return cell_text(cells[col])
    return None


def main():
    service = get_service()
    pres = service.presentations().get(presentationId=PRESENTATION_ID).execute()
    slides = pres['slides']
    print(f'Loaded presentation — {len(slides)} slides')

    all_requests = []

    # ── 1. Slide 3: Fix League Administrators missing newline ─────────────────
    # Shape p3_i82 has "League AdministratorsOversee multiple teams..."
    # Need to insert '\n' after "League Administrators" (21 chars)
    txt_p3i82 = get_shape_text_by_id(slides, 'p3_i82')
    print(f'\n[1] p3_i82 current text: {repr(txt_p3i82[:60])}')
    prefix = 'League Administrators'
    if txt_p3i82 and txt_p3i82.startswith(prefix) and '\n' not in txt_p3i82[:len(prefix) + 1]:
        print(f'    -> Inserting \\n after "{prefix}"')
        all_requests.append({
            'insertText': {
                'objectId': 'p3_i82',
                'insertionIndex': len(prefix),
                'text': '\n'
            }
        })
    else:
        print('    -> Already has newline, skipping')

    # ── 2. Slide 13: Fix legend "45-50%" -> "45%-50%" ────────────────────────
    txt_p13i68 = get_shape_text_by_id(slides, 'p13_i68')
    print(f'\n[2] p13_i68 current text: {repr(txt_p13i68)}')
    old_legend = '45-50%'
    new_legend = '45%-50%'
    if txt_p13i68 and txt_p13i68.startswith(old_legend):
        print(f'    -> Replacing "{old_legend}" with "{new_legend}"')
        all_requests.append({
            'deleteText': {
                'objectId': 'p13_i68',
                'textRange': {'type': 'FIXED_RANGE', 'startIndex': 0, 'endIndex': len(old_legend)}
            }
        })
        all_requests.append({
            'insertText': {
                'objectId': 'p13_i68',
                'insertionIndex': 0,
                'text': new_legend
            }
        })
    else:
        print(f'    -> Text does not match "{old_legend}", skipping')

    # ── 3. Slide 20: Remove "(ON $29.97M ARR)" from title ────────────────────
    txt_p20i4 = get_shape_text_by_id(slides, 'p20_i4')
    print(f'\n[3] p20_i4 current text: {repr(txt_p20i4)}')
    old_title = 'GROSS PROFIT SCENARIOS (ON $29.97M ARR)'
    new_title = 'GROSS PROFIT SCENARIOS'
    if txt_p20i4 and old_title in txt_p20i4:
        print(f'    -> Replacing title text')
        # Delete everything except trailing \n
        content_len = len(old_title)
        all_requests.append({
            'deleteText': {
                'objectId': 'p20_i4',
                'textRange': {'type': 'FIXED_RANGE', 'startIndex': 0, 'endIndex': content_len}
            }
        })
        all_requests.append({
            'insertText': {
                'objectId': 'p20_i4',
                'insertionIndex': 0,
                'text': new_title
            }
        })
    else:
        print(f'    -> Old title not found, skipping')

    # ── 4. Slide 21: Update competitor table ─────────────────────────────────
    # 4a. Row 3 col 0: rename "Sport Coverage" -> "Stats & Video"
    txt_r3c0 = get_table_cell_text(slides, 'p21_i2', 3, 0)
    print(f'\n[4a] p21_i2 [3,0] current: {repr(txt_r3c0)}')
    if txt_r3c0 and txt_r3c0.strip() == 'Sport Coverage':
        print('    -> Renaming to "Stats & Video"')
        old = 'Sport Coverage'
        new = 'Stats & Video'
        all_requests.append({
            'deleteText': {
                'objectId': 'p21_i2',
                'cellLocation': {'rowIndex': 3, 'columnIndex': 0},
                'textRange': {'type': 'FIXED_RANGE', 'startIndex': 0, 'endIndex': len(old)}
            }
        })
        all_requests.append({
            'insertText': {
                'objectId': 'p21_i2',
                'cellLocation': {'rowIndex': 3, 'columnIndex': 0},
                'insertionIndex': 0,
                'text': new
            }
        })

    # 4b. Row 3 col 1: change "Hudl / GameChanger / NCSA" -> "Hudl / GameChanger"
    txt_r3c1 = get_table_cell_text(slides, 'p21_i2', 3, 1)
    print(f'\n[4b] p21_i2 [3,1] current: {repr(txt_r3c1)}')
    old_comp = 'Hudl / GameChanger / NCSA'
    new_comp = 'Hudl / GameChanger'
    if txt_r3c1 and old_comp in txt_r3c1:
        print(f'    -> Replacing "{old_comp}" with "{new_comp}"')
        all_requests.append({
            'deleteText': {
                'objectId': 'p21_i2',
                'cellLocation': {'rowIndex': 3, 'columnIndex': 1},
                'textRange': {'type': 'FIXED_RANGE', 'startIndex': 0, 'endIndex': len(old_comp)}
            }
        })
        all_requests.append({
            'insertText': {
                'objectId': 'p21_i2',
                'cellLocation': {'rowIndex': 3, 'columnIndex': 1},
                'insertionIndex': 0,
                'text': new_comp
            }
        })

    # 4c. Row 3 col 2: update Team Thrive description to focus on stats/video
    txt_r3c2 = get_table_cell_text(slides, 'p21_i2', 3, 2)
    print(f'\n[4c] p21_i2 [3,2] current: {repr(txt_r3c2[:80])}')
    old_desc = 'Inclusive design covering all sports, especially Title IX (Girls) and Boys Athletics and Olympic disciplines.'
    new_desc_stats = 'Built-in performance tracking, video sharing, and athlete stats — accessible to coaches, parents, and athletes in real time.'
    if txt_r3c2 and old_desc in txt_r3c2:
        print('    -> Updating row 3 col 2 to stats/video description')
        all_requests.append({
            'deleteText': {
                'objectId': 'p21_i2',
                'cellLocation': {'rowIndex': 3, 'columnIndex': 2},
                'textRange': {'type': 'FIXED_RANGE', 'startIndex': 0, 'endIndex': len(old_desc)}
            }
        })
        all_requests.append({
            'insertText': {
                'objectId': 'p21_i2',
                'cellLocation': {'rowIndex': 3, 'columnIndex': 2},
                'insertionIndex': 0,
                'text': new_desc_stats
            }
        })

    # 4d. Insert new row 4 (after row 3) for NCSA / SportsRecruits
    print('\n[4d] Inserting new row 4 for NCSA/SportsRecruits')
    all_requests.append({
        'insertTableRows': {
            'tableObjectId': 'p21_i2',
            'cellLocation': {'rowIndex': 3, 'columnIndex': 0},
            'insertBelow': True,
            'number': 1
        }
    })

    # 4e. Fill new row 4 cells
    new_row_data = [
        (4, 0, 'Recruiting'),
        (4, 1, 'NCSA / SportsRecruits'),
        (4, 2, 'Verified athlete profiles, coach-facing highlight reels, and recruiting tools built directly into the platform.')
    ]
    for row_i, col_i, text in new_row_data:
        print(f'    -> Inserting [{row_i},{col_i}]: {repr(text[:60])}')
        all_requests.append({
            'insertText': {
                'objectId': 'p21_i2',
                'cellLocation': {'rowIndex': row_i, 'columnIndex': col_i},
                'insertionIndex': 0,
                'text': text
            }
        })

    # ── 5. Slide 19: Clarify fees are for competition/travel, not monthly tuition ──
    txt_p19i35 = get_shape_text_by_id(slides, 'p19_i35')
    print(f'\n[5] p19_i35 current text: {repr(txt_p19i35)}')
    old_fee_text = 'APPLIED TO ALL PAYMENTS VIA STRIPE'
    new_fee_text = 'APPLIED TO COMPETITION FEES, TRAVEL & CAMPS — NOT MONTHLY TUITION'
    if txt_p19i35 and old_fee_text in txt_p19i35:
        print(f'    -> Updating fee scope description')
        all_requests.append({
            'deleteText': {
                'objectId': 'p19_i35',
                'textRange': {'type': 'FIXED_RANGE', 'startIndex': 0, 'endIndex': len(old_fee_text)}
            }
        })
        all_requests.append({
            'insertText': {
                'objectId': 'p19_i35',
                'insertionIndex': 0,
                'text': new_fee_text
            }
        })
    else:
        print(f'    -> Text not found, skipping')

    # ── 6. Our Team: Update Courtney's description to mention Ronas ───────────
    courtney_oid = 'fix_61fd0309bf8f46bf'
    txt_courtney = get_shape_text_by_id(slides, courtney_oid)
    print(f'\n[6] {courtney_oid} current text: {repr(txt_courtney[:80])}')
    old_courtney_suffix = 'Expert in consumer-grade sports and wellness software at scale.'
    new_courtney_suffix = 'Overseeing development with Ronas, a European mobile dev team building the platform from the ground up.'
    if txt_courtney and old_courtney_suffix in txt_courtney:
        start = txt_courtney.index(old_courtney_suffix)
        end = start + len(old_courtney_suffix)
        print(f'    -> Replacing suffix at [{start}:{end}]')
        all_requests.append({
            'deleteText': {
                'objectId': courtney_oid,
                'textRange': {'type': 'FIXED_RANGE', 'startIndex': start, 'endIndex': end}
            }
        })
        all_requests.append({
            'insertText': {
                'objectId': courtney_oid,
                'insertionIndex': start,
                'text': new_courtney_suffix
            }
        })
    else:
        print(f'    -> Old suffix not found: {repr(old_courtney_suffix[:40])}')

    # ── Apply all changes ─────────────────────────────────────────────────────
    print(f'\nApplying {len(all_requests)} total requests...')
    batch(service, all_requests)
    print('\nAll Wes feedback changes applied successfully.')


if __name__ == '__main__':
    main()
