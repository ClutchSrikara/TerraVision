"""
test_run.py — CLI test runner
Run: python test_run.py

Put your images in data/inputs/:
  blueprint.jpg       ← the blue technical drawing
  site_partial.jpg    ← the partial construction photo
  site_full.jpg       ← the completed room photo (optional)
"""

import os
import sys
import json

from src.pipeline import run_pipeline

MANIFEST = open("data/inputs/materials_manifest.txt").read()

print("\n" + "█" * 55)
print("  PARTIAL PHOTO TEST (should show ~40% complete)")
print("█" * 55)

results = run_pipeline(
    blueprint_path="blueprint.jpeg",
    site_photo_path="photo.jpeg",
    materials_manifest=MANIFEST
)

a = results["analysis"]
if "parse_error" not in a:
    print(f"\nProgress:  {a['progress_percentage']}%")
    print(f"Summary:   {a['progress_summary']}")
    print(f"Missing:   {a['missing_items']}")
    print(f"Needed:    {a['materials_still_needed']}")
    print(f"Next:      {a['next_steps'][0]}")

    # Save output
    os.makedirs("data/outputs", exist_ok=True)
    with open("data/outputs/result_partial.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\n📁 Saved to data/outputs/result_partial.json")
