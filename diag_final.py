#!/usr/bin/env python3
"""Get full table cell text from slide 21 and Our Team slide content."""

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

def shape_text_full(elem):
    parts = []
    for te in elem.get('shape', {}).get('text', {}).get('textElements', []):
        if 'textRun' in te:
            parts.append(te['textRun'].get('content', ''))
    return ''.join(parts)

def cell_text_full(cell):
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
            txt = shape_text_full(elem)
            print(f"{prefix}SHAPE {oid}: {repr(txt)}")
        elif 'elementGroup' in elem:
            print(f"{prefix}GROUP {oid}:")
            sub_elems = elem['elementGroup'].get('children', [])
            dump_elements(sub_elems, indent + 2)
        elif 'image' in elem:
            print(f"{prefix}IMAGE {oid}")
        elif 'table' in elem:
            tbl = elem['table']
            rows = tbl.get('rows', 0)
            cols = tbl.get('columns', 0)
            print(f"{prefix}TABLE {oid} ({rows}x{cols}):")
            for r, row in enumerate(tbl.get('tableRows', [])):
                for c, cell in enumerate(row.get('tableCells', [])):
                    ct = cell_text_full(cell)
                    print(f"{prefix}  [{r},{c}]: {repr(ct)}")

def main():
    service = get_service()
    pres = service.presentations().get(presentationId=PRESENTATION_ID).execute()
    slides = pres['slides']

    print(f"Total slides: {len(slides)}")

    # Slide 21 (index 20)
    print("\n" + "="*60 + "\nSlide 21 (index 20): COMPETITIVE COMPARISON\n" + "="*60)
    dump_elements(slides[20].get('pageElements', []))

    # Slide 19 (index 18): Unit Economics
    print("\n" + "="*60 + "\nSlide 19 (index 18): UNIT ECONOMICS\n" + "="*60)
    dump_elements(slides[18].get('pageElements', []))

    # Our Team slide - find by objectId
    team_slide_id = 'id_28e03f1590b44fbb'
    for i, slide in enumerate(slides):
        if slide['objectId'] == team_slide_id:
            print(f"\n{'='*60}\nOur Team slide (index {i}): {team_slide_id}\n{'='*60}")
            dump_elements(slide.get('pageElements', []))
            break
    else:
        print(f"\nOur Team slide {team_slide_id} not found! Checking by title...")
        for i, slide in enumerate(slides):
            for elem in slide.get('pageElements', []):
                txt = shape_text_full(elem)
                if 'OUR TEAM' in txt.upper():
                    print(f"\n{'='*60}\nOur Team slide (index {i}): {slide['objectId']}\n{'='*60}")
                    dump_elements(slide.get('pageElements', []))
                    break

if __name__ == '__main__':
    main()
