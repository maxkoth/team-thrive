#!/usr/bin/env python3
"""Rebuild the self-contained slideshow.html embedding all carousel slides as base64."""
import base64, glob, os

OUT = "instagram-carousel"
files = sorted(glob.glob(f"{OUT}/slide_*.png"))
n = len(files)

def datauri(p):
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()

imgs = "\n".join(
    f'    <img class="slide{" active" if k==0 else ""}" src="{datauri(f)}" alt="Slide {k+1}">'
    for k, f in enumerate(files)
)
dots = "\n".join(
    f'    <button class="dot{" active" if k==0 else ""}" data-i="{k}" aria-label="Go to slide {k+1}"></button>'
    for k in range(n)
)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Team Thrive — Instagram Carousel</title>
<style>
  :root {{ --navy:#0D1B3E; --green:#3DDC84; }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#070f24; min-height:100vh; display:flex; flex-direction:column;
         align-items:center; justify-content:center; gap:22px;
         font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; color:#fff; padding:24px; }}
  h1 {{ font-size:18px; font-weight:600; letter-spacing:.04em; opacity:.85; }}
  h1 span {{ color:var(--green); }}
  .stage {{ position:relative; width:min(86vw,86vh,640px); aspect-ratio:1/1; border-radius:20px;
            overflow:hidden; box-shadow:0 24px 70px rgba(0,0,0,.6); background:var(--navy); }}
  .slide {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0; transition:opacity .45s ease; }}
  .slide.active {{ opacity:1; }}
  .nav {{ position:absolute; top:50%; transform:translateY(-50%); width:46px; height:46px; border:none;
          border-radius:50%; background:rgba(255,255,255,.12); color:#fff; font-size:22px; cursor:pointer;
          display:flex; align-items:center; justify-content:center; backdrop-filter:blur(6px); transition:background .2s; }}
  .nav:hover {{ background:var(--green); color:var(--navy); }}
  .prev {{ left:14px; }} .next {{ right:14px; }}
  .dots {{ display:flex; gap:10px; flex-wrap:wrap; justify-content:center; max-width:640px; }}
  .dot {{ width:11px; height:11px; border-radius:50%; border:none; background:rgba(255,255,255,.28); cursor:pointer; padding:0; }}
  .dot.active {{ background:var(--green); }}
  .bar {{ display:flex; align-items:center; gap:18px; }}
  .bar button {{ background:rgba(255,255,255,.12); color:#fff; border:none; padding:8px 16px; border-radius:8px; cursor:pointer; font-size:14px; }}
  .bar button:hover {{ background:var(--green); color:var(--navy); }}
  .count {{ font-size:14px; opacity:.75; }}
</style>
</head>
<body>
  <h1>Team <span>Thrive</span> — Instagram Carousel ({n} slides)</h1>
  <div class="stage" id="stage">
{imgs}
    <button class="nav prev" id="prev" aria-label="Previous">‹</button>
    <button class="nav next" id="next" aria-label="Next">›</button>
  </div>
  <div class="dots">
{dots}
  </div>
  <div class="bar">
    <button id="play">▶ Autoplay</button>
    <span class="count"><span id="cur">1</span> / {n}</span>
  </div>
<script>
  const slides=[...document.querySelectorAll('.slide')];
  const dots=[...document.querySelectorAll('.dot')];
  let i=0, timer=null;
  function show(n){{ i=(n+slides.length)%slides.length;
    slides.forEach((s,k)=>s.classList.toggle('active',k===i));
    dots.forEach((d,k)=>d.classList.toggle('active',k===i));
    document.getElementById('cur').textContent=i+1; }}
  document.getElementById('next').onclick=()=>show(i+1);
  document.getElementById('prev').onclick=()=>show(i-1);
  dots.forEach(d=>d.onclick=()=>show(+d.dataset.i));
  document.addEventListener('keydown',e=>{{ if(e.key==='ArrowRight')show(i+1); if(e.key==='ArrowLeft')show(i-1); }});
  const playBtn=document.getElementById('play');
  playBtn.onclick=()=>{{ if(timer){{clearInterval(timer);timer=null;playBtn.textContent='▶ Autoplay';}}
    else{{timer=setInterval(()=>show(i+1),2500);playBtn.textContent='❚❚ Pause';}} }};
  let x0=null; const st=document.getElementById('stage');
  st.addEventListener('touchstart',e=>x0=e.touches[0].clientX);
  st.addEventListener('touchend',e=>{{ if(x0===null)return; const dx=e.changedTouches[0].clientX-x0;
    if(Math.abs(dx)>40) show(dx<0?i+1:i-1); x0=null; }});
</script>
</body>
</html>
"""

open(f"{OUT}/slideshow.html", "w").write(html)
print(f"slideshow.html rebuilt with {n} slides")
