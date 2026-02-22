"""
STEP 4 — Claude Spatial Reasoning
Sends blueprint image, site photo, manifest, and diff to Claude.
Output: structured JSON analysis with progress %, gaps, materials, next steps.
"""

import anthropic
import base64
import json
import os
from io import BytesIO
from PIL import Image


def _to_base64(image_path: str) -> tuple[str, str]:
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
    return b64, "image/jpeg"


def claude_analysis(
    blueprint_path: str,
    photo_path: str,
    materials_manifest: str,
    diff_data: dict
) -> dict:

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.Anthropic(api_key=api_key)

    bp_b64, bp_media = _to_base64(blueprint_path)
    ph_b64, ph_media = _to_base64(photo_path)

    prompt = f"""You are an expert construction site analyst with deep spatial intelligence.

You are given THREE inputs:

IMAGE 1 — BLUEPRINT (the target / finished state)
Key dimensions from this drawing:
- Total wall width: 14'6"
- 2 windows: each 4'6" wide x 5' tall, 4-pane, black aluminum frame
- Counter shelf: 13'6" long x 12" deep
- 3 shelf brackets: spaced 14" apart
- 6 bar stools: alternating 18" / 14" spacing
- 2 electrical outlets mounted between the windows
- Paint: sage green lower half, white upper half
- Flooring: wood laminate

IMAGE 2 — SITE PHOTO (the current / partial state)
This is what has actually been built. Compare it carefully against the blueprint.

MATERIALS MANIFEST:
{materials_manifest}

AUTOMATED DIFF (pre-computed by computer vision):
{json.dumps(diff_data, indent=2)}

YOUR TASK:
For every element in the blueprint, determine whether it is:
  ✅ Completed — present and matches blueprint
  ❌ Missing — not visible at all
  ⚠️  Incorrect — present but wrong size, count, or position

Be specific. Reference exact elements from the blueprint dimensions.

Respond ONLY with valid JSON — no explanation, no markdown, just the JSON object:

{{
  "progress_percentage": <integer 0-100>,
  "progress_summary": "<one clear sentence describing the current build state>",
  "completed_items": [
    "<element that is present and correct>"
  ],
  "missing_items": [
    "<element that is absent>"
  ],
  "incorrect_items": [
    "<element that is present but wrong>"
  ],
  "materials_still_needed": [
    "<material with quantity>"
  ],
  "next_steps": [
    "<most urgent action>",
    "<second action>",
    "<third action>"
  ],
  "spatial_observations": "<detailed note about spatial layout, alignment, and any dimensional concerns>",
  "confidence": "low | medium | high"
}}"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "IMAGE 1 — BLUEPRINT (target state):"},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": bp_media,
                        "data": bp_b64
                    }
                },
                {"type": "text", "text": "IMAGE 2 — SITE PHOTO (current state):"},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": ph_media,
                        "data": ph_b64
                    }
                },
                {"type": "text", "text": prompt}
            ]
        }]
    )

    raw = message.content[0].text
    clean = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"raw_response": raw, "parse_error": True}
