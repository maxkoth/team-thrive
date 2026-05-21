#!/usr/bin/env python3
"""Detailed diagnostic for slides 3 and 13."""

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

def dump_slide_full(slide, idx):
    sid = slide['objectId']
    print(f"\n{'='*60}")
    print(f"Slide {idx+1}: {sid}")
    print(f"{'='*60}")
    for elem in slide.get('pageElements', []):
        oid = elem['objectId']
        if 'shape' in elem:
            txt = shape_text_full(elem)
            print(f"  SHAPE {oid}: {repr(txt[:200])}")
        elif 'table' in elem:
            tbl = elem['table']
            rows = tbl.get('rows', 0)
            cols = tbl.get('columns', 0)
            print(f"  TABLE {oid} ({rows}x{cols})")
        elif 'image' in elem:
            print(f"  IMAGE {oid}")
        elif 'elementGroup' in elem:
            print(f"  GROUP {oid}")
        else:
            print(f"  OTHER {oid}: {list(elem.keys())}")

def main():
    service = get_service()
    pres = service.presentations().get(presentationId=PRESENTATION_ID).execute()
    slides = pres['slides']

    # Slides 3 and 13 (0-indexed: 2 and 12)
    for i in [2, 12]:
        dump_slide_full(slides[i], i)

if __name__ == '__main__':
    main()
