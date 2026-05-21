#!/usr/bin/env python3
"""Verify Wes feedback changes were applied correctly."""

import os
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

def _search_text(elements, oid):
    for elem in elements:
        if elem['objectId'] == oid and 'shape' in elem:
            return shape_text(elem)
        if 'elementGroup' in elem:
            r = _search_text(elem['elementGroup'].get('children', []), oid)
            if r is not None:
                return r
    return None

def get_txt(slides, oid):
    for slide in slides:
        r = _search_text(slide.get('pageElements', []), oid)
        if r is not None:
            return r
    return None

def main():
    service = get_service()
    pres = service.presentations().get(presentationId=PRESENTATION_ID).execute()
    slides = pres['slides']

    print('=== Verification of Wes Feedback Changes ===\n')

    # 1. Slide 3 League Administrators
    t = get_txt(slides, 'p3_i82')
    ok = t and t.startswith('League Administrators\n')
    print(f'[1] Slide 3 - League Admin newline: {"✓ PASS" if ok else "✗ FAIL"}')
    print(f'    {repr(t[:60])}')

    # 2. Slide 13 legend
    t = get_txt(slides, 'p13_i68')
    ok = t and t.startswith('45%-50%')
    print(f'\n[2] Slide 13 - Legend "45%-50%": {"✓ PASS" if ok else "✗ FAIL"}')
    print(f'    {repr(t)}')

    # 3. Slide 20 title
    t = get_txt(slides, 'p20_i4')
    ok = t and '(ON $29.97M ARR)' not in t and 'GROSS PROFIT SCENARIOS' in t
    print(f'\n[3] Slide 20 - Title without ARR: {"✓ PASS" if ok else "✗ FAIL"}')
    print(f'    {repr(t)}')

    # 4. Slide 21 table
    s21 = slides[20]
    for elem in s21.get('pageElements', []):
        if elem['objectId'] == 'p21_i2' and 'table' in elem:
            tbl = elem['table']
            rows = tbl.get('tableRows', [])
            num_rows = len(rows)
            print(f'\n[4] Slide 21 - Competitor table ({num_rows} rows):')
            for r, row in enumerate(rows):
                cells = row.get('tableCells', [])
                row_texts = [cell_text(c).strip() for c in cells]
                print(f'    Row {r}: {row_texts}')
            ok_rows = num_rows == 5
            ok_r3 = len(rows) > 3 and cell_text(rows[3]['tableCells'][1]).strip() == 'Hudl / GameChanger'
            ok_r4 = len(rows) > 4 and 'NCSA' in cell_text(rows[4]['tableCells'][1])
            print(f'    5 rows: {"✓" if ok_rows else "✗"} | Row 3 = Hudl/GameChanger: {"✓" if ok_r3 else "✗"} | Row 4 = NCSA: {"✓" if ok_r4 else "✗"}')

    # 5. Slide 19 fee clarity
    t = get_txt(slides, 'p19_i35')
    ok = t and 'COMPETITION FEES' in t and 'TUITION' in t
    print(f'\n[5] Slide 19 - Fee scope clarification: {"✓ PASS" if ok else "✗ FAIL"}')
    print(f'    {repr(t)}')

    # 6. Our Team Courtney description
    t = get_txt(slides, 'fix_61fd0309bf8f46bf')
    ok = t and 'Ronas' in t
    print(f'\n[6] Our Team - Courtney mentions Ronas: {"✓ PASS" if ok else "✗ FAIL"}')
    print(f'    {repr(t[:100])}')

if __name__ == '__main__':
    main()
