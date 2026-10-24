#!/usr/bin/env python3
"""Phase 3 · AI Video slide, built with the carousel's own builder."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("bps", "build_phase_slides.py")
bps = importlib.util.module_from_spec(spec); sys.modules["bps"] = bps
spec.loader.exec_module(bps)

print("built", bps.build(98, "PHASE 3 · AI VIDEO", "AI VIDEO FEEDBACK",
    ("concept/ai_upload.png", "Upload a Clip",    "A parent uploads ten seconds after practice"),
    ("concept/ai.png",        "Instant Feedback", "The AI reads the technique and saves it")))
