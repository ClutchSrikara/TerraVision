"""
STEP 1 — Blueprint Processing
Uses OpenCV to extract structural elements from the blueprint image.
Output: structured dict describing what SHOULD be present.
"""

import cv2
import numpy as np


def process_blueprint(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Detect lines
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180,
        threshold=80, minLineLength=50, maxLineGap=10
    )

    # Detect rectangles (windows, doors, openings)
    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    rectangles = []
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            area = w * h
            if area > 5000:
                rectangles.append({
                    "x": int(x), "y": int(y),
                    "width": int(w), "height": int(h),
                    "area": int(area)
                })

    rectangles.sort(key=lambda r: r["area"], reverse=True)

    # Count line directions
    h_lines, v_lines = 0, 0
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            if angle < 20 or angle > 160:
                h_lines += 1
            elif 70 < angle < 110:
                v_lines += 1

    large_openings = len([r for r in rectangles if r["area"] > 20000])

    return {
        "structural_rectangles": rectangles[:10],
        "horizontal_lines": h_lines,
        "vertical_lines": v_lines,
        "large_openings": large_openings,
        "total_regions": len(rectangles),
        "summary": (
            f"{len(rectangles)} regions | "
            f"{h_lines}H / {v_lines}V lines | "
            f"{large_openings} large openings"
        )
    }
