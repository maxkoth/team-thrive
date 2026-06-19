# Team Thrive — Interactive Demo (Phase 2)

Purpose: a click-through prototype the founder (Aliza) screen-shares or records to
show coaches the new Phase 2 features. This is NOT the production app — RonasIT
builds that in React Native. Faithfulness to the real designs beats novelty.

## Repo layout
- index.html      — self-contained (HTML/CSS/JS). Six guided tours + explore grid.
- screens/        — 119 real Phase 2 PNGs. Source of truth for layout. Don't edit.
- assets/         — real brand files (logo, wordmark, icon, video). See assets/README.
- README.md       — how to run/host/record.

## Brand
- Navy #0D1B3E, green #3DDC84, near-white text. Confirm exact hexes from Figma.
- Use the real logo in /assets. NEVER use the placeholder shield or the "Red Hawks"
  team logo baked into the screenshots — those are mock data.

## Rules for changes
- Keep it runnable with zero install (open index.html) AND deployable as static.
- Keep the screens as IMAGES. Do not rebuild them as coded components.
- No false claims: the deep-link invite flow is shown as the *intended* corrected
  flow, not "works in the live app today."
- Verify before commit: open index.html and click through one full tour.
- Never commit *.zip or secrets. Brand assets only in /assets.

## Git
- main is the demo. Make changes on a branch, open a PR, don't force-push.
