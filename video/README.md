# Team Thrive — Brand Promo Video

A 30-second, brand-matched promo video for Team Thrive, built as a fully
reproducible, code-driven motion-graphics project (HTML/CSS animation →
frames → MP4). No paid software required.

**Output:** [`team-thrive-promo.mp4`](team-thrive-promo.mp4) — 1280×720, 30 fps, H.264 + AAC.

## What's inside

| File | Purpose |
|------|---------|
| `index.html` | The animation. A deterministic timeline driven by a `render(t)` function — every visual is computed from time `t`, so it renders frame-accurately. Edit text, colors, and timings here. |
| `render.js` | Headless-Chromium (Playwright) renderer. Steps through 0→30 s at 30 fps and screenshots each frame into `out/`. |
| `assets/` | Brand assets: logo lockup + badge (`logo_lockup.png`, `badge.png`), app screen (`app.png`), soundtrack (`audio.m4a`), and fonts (Anton + Barlow Condensed + Inter). |

## Scenes (timeline)

1. **0–4 s** — `EVERY TEAM.` kinetic type on white
2. **4–7.6 s** — `EVERY ATHLETE.` on black
3. **7.6–11.4 s** — `SCHEDULE. CONNECT. THRIVE.`
4. **11.4–20.2 s** — App showcase + feature chips (Smart Calendar / Roster & RSVPs / Instant Updates)
5. **20.2–25.2 s** — `PLAN PRACTICES / TRACK EVERY GAME / RALLY YOUR TEAM`
6. **25.2–30 s** — Logo reveal + CTA

## Re-render it yourself

```bash
cd video
npm install playwright
npx playwright install chromium

# 1. render frames (writes out/f_0000.png … out/f_0899.png)
node render.js          # add --preview for a quick 6-frame check

# 2. encode to MP4 with the soundtrack
ffmpeg -framerate 30 -i out/f_%04d.png -i assets/audio.m4a \
  -map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium \
  -movflags +faststart -c:a aac -b:a 160k -shortest team-thrive-promo.mp4 -y
```

## Customising

- **Copy / colors / timing:** all in `index.html`. Brand colors: green `#3DDC84`,
  teal `#2BB5A0`, navy `#0D1B3E`.
- **Swap in real footage:** this version is pure motion graphics (no licensed
  stock b-roll). To match the original's athlete shots, drop video clips into a
  scene as a `<video>`/background layer in `index.html`, or composite them in a
  video editor over these graphics. Royalty-free sources: Pexels, Pixabay,
  Mixkit (free) or Artgrid / Storyblocks (paid).
- **Different music:** replace `assets/audio.m4a`.
