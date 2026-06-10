#!/usr/bin/env python3
"""Export the carousel source frames from Figma into work/screens/.

Reads the node IDs and output screen names from slides_manifest.json, asks the
Figma REST API to render each node as a 2x PNG, and downloads the results to
work/screens/<screen>.png so build_slides.py can compose the carousel.

Requires network access to:
  - api.figma.com                                  (REST API)
  - figma-alpha-api.s3.us-west-2.amazonaws.com     (rendered PNG download)

Usage:
  FIGMA_TOKEN=figd_... python figma_export.py
  FIGMA_TOKEN=figd_... FIGMA_FILE_KEY=... python figma_export.py
"""
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "slides_manifest.json")
OUT_DIR = os.path.join(ROOT, "work", "screens")

# File key from the Figma design URL:
# https://www.figma.com/design/<FILE_KEY>/Team-Thrive-React-native
FILE_KEY = os.environ.get("FIGMA_FILE_KEY", "Ch5F8G90eeggHnx03jFl15")
TOKEN = os.environ.get("FIGMA_TOKEN")
SCALE = os.environ.get("FIGMA_SCALE", "2")


def api_get(url):
    req = urllib.request.Request(url, headers={"X-Figma-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    if not TOKEN:
        sys.exit("error: set FIGMA_TOKEN (Figma personal access token, file-read scope)")

    manifest = json.load(open(MANIFEST))
    os.makedirs(OUT_DIR, exist_ok=True)

    # Figma node IDs are colon-separated in the API; the manifest stores the
    # dash form used in share URLs (e.g. 35027-28767 -> 35027:28767).
    id_map = {item["node"].replace("-", ":"): item for item in manifest}
    ids = ",".join(id_map.keys())

    print(f"requesting {len(id_map)} renders from file {FILE_KEY} at {SCALE}x ...")
    resp = api_get(
        f"https://api.figma.com/v1/images/{FILE_KEY}"
        f"?ids={ids}&format=png&scale={SCALE}"
    )
    if resp.get("err"):
        sys.exit(f"figma api error: {resp['err']}")

    images = resp.get("images", {})
    missing = [nid for nid in id_map if not images.get(nid)]
    if missing:
        sys.exit(f"error: figma returned no render for nodes: {missing}")

    for nid, url in images.items():
        item = id_map[nid]
        out = os.path.join(OUT_DIR, item["screen"])
        for attempt in range(4):
            try:
                urllib.request.urlretrieve(url, out)
                break
            except Exception as e:  # noqa: BLE001 - retry transient download errors
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        print(f"  {item['node']:>12}  ->  {os.path.relpath(out, ROOT)}  ({item['headline']})")

    print("done. now run: python build_slides.py")


if __name__ == "__main__":
    main()
