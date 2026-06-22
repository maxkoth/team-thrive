#!/usr/bin/env bash
# Composite athlete footage behind the kinetic-type scenes and render the final MP4.
#
# Usage:
#   1) put clips in  video/clips/  (any .mp4/.mov, named so they sort in order)
#   2) node render.js --overlay        # render RGBA graphics into out_overlay/
#   3) ./compose.sh                    # build footage bed + overlay + audio -> final
#
# Footage windows (seconds) map to the 4 footage scenes; clips cycle if you supply
# fewer than 4. Scenes 4 (app) and 6 (logo) stay clean — no footage.
set -euo pipefail
cd "$(dirname "$0")"

FF="$(command -v ffmpeg || python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
OUT="team-thrive-promo-footage.mp4"

# scene footage windows (start end), padded to cover crossfades
WIN=( "0.0 4.2" "3.8 7.8" "7.4 11.6" "20.0 25.4" )

mapfile -t CLIPS < <(ls clips/*.mp4 clips/*.mov clips/*.MOV clips/*.MP4 2>/dev/null || true)
[ ${#CLIPS[@]} -gt 0 ] || { echo "No clips in clips/. Add some and re-run."; exit 1; }
[ -d out_overlay ] || { echo "out_overlay/ missing. Run: node render.js --overlay"; exit 1; }
echo "Using ${#CLIPS[@]} clip(s) across ${#WIN[@]} footage windows."

# Pre-encode the RGBA PNG sequence to a constant-format alpha video first.
# (Mixed RGB/RGBA PNGs make ffmpeg reconfigure the filtergraph every frame.)
GFX="gfx_overlay.mov"
if [ ! -f "$GFX" ] || [ "$(ls -t out_overlay/f_0899.png "$GFX" 2>/dev/null | head -1)" != "$GFX" ]; then
  echo "Building constant-format alpha overlay -> $GFX"
  "$FF" -framerate 30 -i out_overlay/f_%04d.png \
    -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le "$GFX" -y >/dev/null 2>&1
fi

# Build ffmpeg inputs: one per window (clips cycle), then the graphics PNG sequence, then audio.
inputs=(); filt=""; prev="[base]"
filt+="color=c=black:s=1280x720:r=30:d=30[base];"
for i in "${!WIN[@]}"; do
  clip="${CLIPS[$(( i % ${#CLIPS[@]} ))]}"
  inputs+=( -stream_loop -1 -i "$clip" )
  read -r A B <<< "${WIN[$i]}"
  D=$(awk "BEGIN{print $B-$A}")
  # trim, cover-scale to fill 1280x720, place at window start
  filt+="[$i:v]trim=0:${D},setpts=PTS-STARTPTS,fps=30,"
  filt+="scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
  filt+="setpts=PTS-STARTPTS+${A}/TB[c$i];"
  filt+="${prev}[c$i]overlay=enable='between(t,${A},${B})':eof_action=pass[b$i];"
  prev="[b$i]"
done
g=${#WIN[@]}                 # graphics input index
a=$((g+1))                   # audio input index
inputs+=( -i "$GFX" )
inputs+=( -i assets/audio.m4a )
filt+="${prev}[${g}:v]overlay=0:0:eof_action=pass[v]"

"$FF" "${inputs[@]}" -filter_complex "$filt" \
  -map "[v]" -map "${a}:a" -t 30 \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -movflags +faststart \
  -c:a aac -b:a 160k "$OUT" -y

echo "Done -> $OUT"
