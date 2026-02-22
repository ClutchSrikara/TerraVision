"""
STEP 3 — Three-Way Spatial Diff
Compares blueprint data vs photo detections vs materials manifest.
Output: structured diff with flags and estimated progress %.
"""


def compute_diff(
    blueprint_data: dict,
    photo_data: dict,
    materials_manifest: str
) -> dict:

    # Parse manifest into clean line items
    manifest_items = [
        line.strip()
        for line in materials_manifest.strip().split("\n")
        if line.strip()
        and not line.strip().isupper()
        and not line.strip().startswith("#")
        and "---" not in line
        and not line.strip().startswith("ROOM")
        and not line.strip().startswith("Total")
    ]

    # Compare openings
    bp_openings = blueprint_data.get("large_openings", 0)
    ph_openings = (
        photo_data["class_counts"].get("window_opening", 0) +
        photo_data["class_counts"].get("window", 0)
    )
    opening_gap = max(bp_openings - ph_openings, 0)

    # Estimate overall completeness
    bp_regions = blueprint_data.get("total_regions", 1)
    ph_regions = photo_data.get("total_objects", 0)
    completeness = min(ph_regions / max(bp_regions, 1), 1.0)
    estimated_pct = round(completeness * 100)

    # Generate flags
    flags = []
    if opening_gap > 0:
        flags.append(f"⚠️  {opening_gap} opening(s) in blueprint not found in photo")
    if estimated_pct < 40:
        flags.append("❌ Early stage — under 40% of blueprint complexity present")
    elif estimated_pct < 75:
        flags.append("🔨 Mid stage — 40–75% of blueprint complexity present")
    else:
        flags.append("✅ Advanced stage — photo closely matches blueprint")

    return {
        "blueprint_summary": blueprint_data["summary"],
        "photo_summary": photo_data["summary"],
        "manifest_items": manifest_items,
        "structural_comparison": {
            "blueprint_openings": bp_openings,
            "detected_openings": ph_openings,
            "missing_openings": opening_gap,
            "blueprint_regions": bp_regions,
            "detected_regions": ph_regions,
        },
        "estimated_progress_pct": estimated_pct,
        "flags": flags
    }
