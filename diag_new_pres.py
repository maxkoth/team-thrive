#!/usr/bin/env python3
"""Full diagnostic of new presentation to map element IDs for all planned changes."""

import os
import httplib2
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as SACredentials
import google_auth_httplib2

NEW_PRES_ID = '1nZ1YfTqSUfzsBbzZC8azxza9XoPZ66mfJI2fXHOwIIo'
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

def dump_elements(elements, indent=2):
    for elem in elements:
        oid = elem['objectId']
        prefix = ' ' * indent
        if 'shape' in elem:
            txt = shape_text(elem)
            if txt.strip():
                print(f"{prefix}SHAPE {oid}: {repr(txt[:120])}")
            else:
                print(f"{prefix}SHAPE {oid}: (empty)")
        elif 'table' in elem:
            tbl = elem['table']
            rows = tbl.get('rows', 0)
            cols = tbl.get('columns', 0)
            print(f"{prefix}TABLE {oid} ({rows}x{cols}):")
            for r, row in enumerate(tbl.get('tableRows', [])):
                for c, cell in enumerate(row.get('tableCells', [])):
                    ct = cell_text(cell)
                    if ct.strip():
                        print(f"{prefix}  [{r},{c}]: {repr(ct[:100])}")
        elif 'elementGroup' in elem:
            print(f"{prefix}GROUP {oid}:")
            dump_elements(elem['elementGroup'].get('children', []), indent + 2)
        elif 'image' in elem:
            print(f"{prefix}IMAGE {oid}")
        else:
            print(f"{prefix}OTHER {oid}: {list(elem.keys())}")

def main():
    service = get_service()
    pres = service.presentations().get(presentationId=NEW_PRES_ID).execute()
    slides = pres['slides']
    print(f"Total slides: {len(slides)}")
    print(f"Slide size: {pres.get('pageSize', {})}")

    for i, slide in enumerate(slides):
        sid = slide['objectId']
        # Find the title text for this slide
        title_txt = ''
        for elem in slide.get('pageElements', []):
            t = shape_text(elem) if 'shape' in elem else ''
            if t.strip() and len(t.strip()) < 80:
                title_txt = t.strip()[:60]
                break
        print(f"\n{'='*60}")
        print(f"Slide {i+1} [{sid}]: {title_txt}")
        print(f"{'='*60}")
        dump_elements(slide.get('pageElements', []))

if __name__ == '__main__':
    main()
