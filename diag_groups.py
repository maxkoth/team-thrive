#!/usr/bin/env python3
"""Recursive diagnostic for slides 3 and 13, looking inside groups."""

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

def dump_elements(elements, indent=2):
    for elem in elements:
        oid = elem['objectId']
        prefix = ' ' * indent
        if 'shape' in elem:
            txt = shape_text_full(elem)
            print(f"{prefix}SHAPE {oid}: {repr(txt[:150])}")
        elif 'elementGroup' in elem:
            print(f"{prefix}GROUP {oid}:")
            sub_elems = elem['elementGroup'].get('children', [])
            dump_elements(sub_elems, indent + 2)
        elif 'image' in elem:
            print(f"{prefix}IMAGE {oid}")
        elif 'table' in elem:
            print(f"{prefix}TABLE {oid}")
        else:
            print(f"{prefix}OTHER {oid}: {list(elem.keys())}")

def dump_slide(slide, idx):
    sid = slide['objectId']
    print(f"\n{'='*60}")
    print(f"Slide {idx+1}: {sid}")
    print(f"{'='*60}")
    dump_elements(slide.get('pageElements', []))

def main():
    service = get_service()
    pres = service.presentations().get(presentationId=PRESENTATION_ID).execute()
    slides = pres['slides']

    for i in [2, 12]:
        dump_slide(slides[i], i)

if __name__ == '__main__':
    main()
