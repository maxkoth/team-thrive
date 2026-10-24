#!/usr/bin/env python3
"""Rebuild the Notes and AI slides on Ronas's actual Phase 3 designs."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("bps", "build_phase_slides.py")
bps = importlib.util.module_from_spec(spec); sys.modules["bps"] = bps
spec.loader.exec_module(bps)

print(bps.build(99, "PHASE 3 · FIRST UP", "NOTES & JOURNAL",
    ("concept/p3_profile_notes.png", "Three Voices",  "Coach, parent and athlete notes on one profile"),
    ("concept/p3_note_athlete.png",  "Who Sees What", "Shared with the coach, or kept private")))

# the real design is an assistant that reads the whole record, not one-shot clip analysis
print(bps.build(98, "PHASE 3 · AI ANALYSIS", "ASK ANYTHING",
    ("concept/p3_ai_chat.png",  "Your AI Analyst", "Recruiting odds, progress, what to work on"),
    ("concept/p3_ai_video.png", "Clip Breakdown",  "Upload a clip, get technique feedback")))
