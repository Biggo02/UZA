"""Fast, local-first visual recognition for UZA.

The recognizer is category-first. It can recognize an object from shape and
appearance even when no logo, label or readable text is present. OCR is not
part of the initial recognition path.
"""
import os
from functools import lru_cache

CATEGORY_LABELS = {
    "Smartphones": ["smartphone", "mobile phone"],
    "Téléphones classiques": ["feature phone", "keypad mobile phone"],
    "Ordinateurs portables": ["laptop", "notebook computer"],
    "Ordinateurs de bureau": ["desktop computer", "desktop PC"],
    "Tablettes": ["tablet computer", "tablet"],
    "Téléviseurs": ["flat screen television", "television"],
    "Consoles de jeux": ["video game console", "gaming console"],
    "Appareils photo": ["digital camera", "photography camera"],
    "Caméras": ["video camera", "camcorder"],
    "Audio / enceintes / casques": ["speaker", "headphones"],
    "Montres connectées": ["smartwatch", "smart watch"],
    "Réfrigérateurs": ["refrigerator", "fridge"],
    "Congélateurs": ["freezer", "chest freezer"],
    "Machines à laver": ["washing machine", "clothes washer"],
    "Fours": ["kitchen oven", "electric oven"],
    "Micro-ondes": ["microwave oven", "microwave"],
    "Climatiseurs": ["air conditioner", "split air conditioner"],
    "Ventilateurs": ["electric fan", "standing fan"],
    "Petits appareils électroménagers": ["small home appliance", "kitchen appliance"],
    "Accessoires électroniques": ["electronic accessory", "computer accessory"],
}


@lru_cache(maxsize=1)
def _local_model():
    """Load the model once per worker instead of once per request."""
    from transformers import CLIPModel, CLIPProcessor
    name = os.environ.get("UZA_LOCAL_VISION_MODEL", "openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained(name)
    model = CLIPModel.from_pretrained(name)
    model.eval()
    return processor, model


def _read_image(uploaded):
    """Decode only one bounded image at a time."""
    from PIL import Image
    uploaded.seek(0)
    with Image.open(uploaded) as source:
        source.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
        return source.convert("RGB").copy()


def _local_analyze(files):
    import torch

    processor, model = _local_model()
    labels = list(CATEGORY_LABELS)
    prompts = [
        f"a clear product photo of {CATEGORY_LABELS[label][0]}"
        for label in labels
    ]
    aggregate = torch.zeros(len(labels), dtype=torch.float32)

    # Text embeddings are identical for every photo: calculate them once.
    with torch.inference_mode():
        text_inputs = processor(text=prompts, return_tensors="pt", padding=True)
        text_features = model.get_text_features(**text_inputs)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        for uploaded in files:
            image = _read_image(uploaded)
            image_inputs = processor(images=image, return_tensors="pt")
            image_features = model.get_image_features(**image_inputs)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            scores = (image_features @ text_features.T).squeeze(0)
            aggregate += torch.softmax(scores * 12.0, dim=0).detach().cpu()
            del image_inputs, image_features, scores, image

        del text_inputs, text_features

    aggregate /= max(1, len(files))
    values, indices = torch.topk(aggregate, k=min(5, len(labels)))
    candidates = [
        {"category": labels[int(i)], "confidence": round(float(v) * 100, 1)}
        for v, i in zip(values, indices)
    ]
    best = candidates[0]
    return {
        "status": "READY",
        "engine": "LOCAL_CLIP_FAST",
        "photo_count": 5,
        "object": best["category"],
        "category": best["category"],
        "brand": None,
        "model": None,
        "confidence": best["confidence"],
        "candidates": candidates,
        "evidence": [
            "Silhouette, forme, proportions et apparence générale analysées.",
            "Les cinq vues sont combinées comme un seul produit.",
            "La reconnaissance ne dépend pas d'un logo, d'une étiquette ou d'un texte.",
        ],
        "uncertainty": "La marque et le modèle restent vides sans preuve visuelle suffisante.",
        "message": "Identification visuelle terminée. Vérifiez la catégorie proposée avant de compléter la fiche.",
    }


def analyze_images(files):
    if len(files) != 5:
        return {"status": "ERROR", "message": "UZA exige exactement 5 photos.", "photo_count": len(files)}
    try:
        return _local_analyze(files)
    except Exception as exc:
        return {
            "status": "LOCAL_UNAVAILABLE",
            "engine": "LOCAL_CLIP_FAST",
            "confidence": 0,
            "object": None,
            "category": None,
            "brand": None,
            "model": None,
            "photo_count": 5,
            "message": "Reconnaissance automatique indisponible. Vous pouvez continuer avec une identification manuelle.",
            "technical_detail": str(exc),
        }
