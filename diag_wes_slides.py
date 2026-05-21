#!/usr/bin/env python3
"""Diagnostic: read slides 2, 3, 13, 18-21 to prepare Wes feedback changes."""

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

def dump_slide(slide, idx):
    sid = slide['objectId']
    print(f"\n{'='*60}")
    print(f"Slide {idx+1}: {sid}")
    print(f"{'='*60}")
    for elem in slide.get('pageElements', []):
        oid = elem['objectId']
        if 'shape' in elem:
            txt = shape_text(elem)
            if txt.strip():
                print(f"  SHAPE {oid}: {repr(txt[:120])}")
        elif 'table' in elem:
            tbl = elem['table']
            rows = tbl.get('rows', 0)
            cols = tbl.get('columns', 0)
            print(f"  TABLE {oid} ({rows}x{cols}):")
            for r, row in enumerate(tbl.get('tableRows', [])):
                for c, cell in enumerate(row.get('tableCells', [])):
                    ct = cell_text(cell)
                    if ct.strip():
                        print(f"    [{r},{c}]: {repr(ct[:80])}")

def main():
    service = get_service()
    pres = service.presentations().get(presentationId=PRESENTATION_ID).execute()
    slides = pres['slides']
    print(f"Total slides: {len(slides)}")

    # We want slides at indices 1,2,12,17,18,19,20 (0-indexed = slides 2,3,13,18,19,20,21)
    target_indices = [1, 2, 12, 17, 18, 19, 20]
    for i in target_indices:
        if i < len(slides):
            dump_slide(slides[i], i)

if __name__ == '__main__':
    main()
