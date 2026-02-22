"""
STEP 2 — Site Photo Processing
Uses YOLOv8 to detect objects in the site photo.
Falls back to OpenCV if YOLOv8 is not installed.
Output: structured dict of what IS present on site.
"""

import cv2
import numpy as np


def process_site_photo(image_path: str) -> dict:
    try:
        from ultralytics import YOLO
        return _yolo(image_path)
    except ImportError:
        print("   [INFO] YOLOv8 not found — using OpenCV fallback")
        return _opencv(image_path)


def _yolo(image_path: str) -> dict:
    from ultralytics import YOLO
    model = YOLO("yolov8n.pt")  # auto-downloads on first run (~6MB)
    results = model(image_path, verbose=False)

    detections = []
    class_counts = {}

    for result in results:
        for box in result.boxes:
            name = result.names[int(box.cls)]
            conf = float(box.conf)
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            if conf > 0.3:
                detections.append({
                    "class": name,
                    "confidence": round(conf, 2),
                    "bbox": {
                        "x1": int(x1), "y1": int(y1),
                        "x2": int(x2), "y2": int(y2)
                    }
                })
                class_counts[name] = class_counts.get(name, 0) + 1

    return {
        "method": "yolov8",
        "detections": detections,
        "class_counts": class_counts,
        "total_objects": len(detections),
        "summary": (
            f"YOLOv8: {len(detections)} objects — " +
            ", ".join(f"{v}x {k}" for k, v in class_counts.items())
        )
    }


def _opencv(image_path: str) -> dict:
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h_img, w_img = img.shape[:2]

    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    regions = []
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
        x, y, w, h = cv2.boundingRect(approx)
        area = w * h
        if area > 3000:
            ar = w / h if h > 0 else 0
            rtype = (
                "window_opening"
                if (0.8 < ar < 2.5 and area > 15000)
                else "structural_element"
            )
            regions.append({
                "type": rtype,
                "area": int(area),
                "position": {
                    "x": int(x), "y": int(y),
                    "w": int(w), "h": int(h)
                },
                "zone": "upper" if y < h_img // 2 else "lower"
            })

    regions.sort(key=lambda r: r["area"], reverse=True)
    windows = [r for r in regions if r["type"] == "window_opening"]

    return {
        "method": "opencv_fallback",
        "detections": regions[:15],
        "class_counts": {
            "window_opening": len(windows),
            "structural_element": len(regions) - len(windows)
        },
        "total_objects": len(regions),
        "summary": (
            f"OpenCV: {len(windows)} window openings, "
            f"{len(regions)} total structural regions"
        )
    }
