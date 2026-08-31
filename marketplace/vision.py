"""Vision-provider boundary for UZA.

Visual recognition must use the five photos as a single set. This module keeps the
application safe: when no vision provider is configured, it returns a pending result
rather than inventing a brand or model.
"""

def analyze_images(files):
    return {
        "status": "PENDING_VISION",
        "confidence": 0,
        "object": None,
        "category": None,
        "brand": None,
        "model": None,
        "message": "Analyse visuelle en attente. Le moteur pourra identifier la catégorie même sans logo ni étiquette.",
        "photo_count": len(files),
    }
