import os, httplib2, json, google_auth_httplib2
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as SA

PRES = '1nZ1YfTqSUfzsBbzZC8azxza9XoPZ66mfJI2fXHOwIIo'
SCOPES = ['https://www.googleapis.com/auth/presentations']

def get_svc():
    key = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')
    creds = SA.from_service_account_file(key, scopes=SCOPES)
    h = httplib2.Http(ca_certs='/etc/ssl/certs/ca-certificates.crt')
    return build('slides', 'v1', http=google_auth_httplib2.AuthorizedHttp(creds, http=h))

def shape_text(elem):
    parts = []
    for te in elem.get('shape', {}).get('text', {}).get('textElements', []):
        if 'textRun' in te:
            parts.append(te['textRun'].get('content', ''))
    return ''.join(parts)

svc = get_svc()
pres = svc.presentations().get(presentationId=PRES).execute()
slides = pres['slides']
print(f'Total slides: {len(slides)}')

slide36 = slides[35]  # 0-indexed
print(f'\nSlide 36 objectId: {slide36["objectId"]}')
print(f'Elements ({len(slide36.get("pageElements",[]))}):')
for el in slide36.get('pageElements', []):
    oid = el['objectId']
    kind = list(el.keys() - {'objectId','size','transform','title','description'})
    txt = shape_text(el)[:80] if 'shape' in el else ''
    print(f'  {oid}: {kind} | {repr(txt)}')
    if 'elementGroup' in el:
        for child in el['elementGroup'].get('children', []):
            ctxt = shape_text(child)[:60]
            print(f'    child {child["objectId"]}: {repr(ctxt)}')
