#!/usr/bin/env python3
"""Phase 3 · Notes & Journal slide, built with the carousel's own builder."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("bps", "build_phase_slides.py")
bps = importlib.util.module_from_spec(spec); sys.modules["bps"] = spec.loader.exec_module and bps
spec.loader.exec_module(bps)

out = bps.build(99, "PHASE 3 · FIRST UP", "NOTES & JOURNAL",
    ("concept/notes.png",    "Shared Notes",  "Coach, parent and athlete notes on one profile"),
    ("concept/note_new.png", "Who Sees What", "Every note: shared with the coach, or private"))
print("built", out)
