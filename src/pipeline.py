"""
TerraVision — Main Pipeline Orchestrator
Calls all 4 steps in sequence and returns the full result.
"""

from src.blueprint import process_blueprint
from src.photo import process_site_photo
from src.diff import compute_diff
from src.claude import claude_analysis


def run_pipeline(
    blueprint_path: str,
    site_photo_path: str,
    materials_manifest: str
) -> dict:

    print("\n" + "=" * 55)
    print("  TERRAVISION — SPATIAL INTELLIGENCE PIPELINE")
    print("=" * 55)

    # STEP 1
    print("\n📐  Step 1 — Blueprint processing (OpenCV)...")
    blueprint_data = process_blueprint(blueprint_path)
    print(f"    → {blueprint_data['summary']}")

    # STEP 2
    print("\n📸  Step 2 — Site photo detection (YOLOv8)...")
    photo_data = process_site_photo(site_photo_path)
    print(f"    → {photo_data['summary']}")

    # STEP 3
    print("\n🔍  Step 3 — Three-way spatial diff...")
    diff_data = compute_diff(blueprint_data, photo_data, materials_manifest)
    print(f"    → Estimated progress: {diff_data['estimated_progress_pct']}%")
    for flag in diff_data["flags"]:
        print(f"    → {flag}")

    # STEP 4
    print("\n🤖  Step 4 — Claude spatial reasoning...")
    analysis = claude_analysis(
        blueprint_path,
        site_photo_path,
        materials_manifest,
        diff_data
    )

    if "parse_error" not in analysis:
        print(f"    → Progress:    {analysis.get('progress_percentage')}%")
        print(f"    → Missing:     {len(analysis.get('missing_items', []))} items")
        print(f"    → Confidence:  {analysis.get('confidence')}")

    print("\n✅  Pipeline complete.")
    print("=" * 55 + "\n")

    return {
        "blueprint_data": blueprint_data,
        "photo_data": photo_data,
        "diff_data": diff_data,
        "analysis": analysis
    }
