"""Local-first visual recognition for UZA.

The local engine uses an open CLIP vision model for zero-shot visual classification.
OCR is only a secondary clue. A missing logo/label must never prevent object/category
recognition. OpenAI is an optional fallback, never the default.
"""
import base64
import json
import mimetypes
import os
import re
from functools import lru_cache

import requests

CATEGORY_LABELS = {
    "Smartphones": ["smartphone", "téléphone portable", "mobile phone"],
    "Téléphones classiques": ["feature phone", "téléphone classique"],
    "Ordinateurs portables": ["laptop", "ordinateur portable"],
    "Ordinateurs de bureau": ["desktop computer", "ordinateur de bureau"],
    "Tablettes": ["tablet computer", "tablette"],
    "Téléviseurs": ["television", "TV écran plat", "smart TV"],
    "Consoles de jeux": ["game console", "console de jeux"],
    "Appareils photo": ["digital camera", "appareil photo"],
    "Caméras": ["video camera", "caméscope", "camera"],
    "Audio / enceintes / casques": ["speaker", "headphones", "audio equipment", "enceinte"],
    "Montres connectées": ["smartwatch", "montre connectée"],
    "Réfrigérateurs": ["refrigerator", "fridge", "réfrigérateur"],
    "Congélateurs": ["freezer", "congélateur"],
    "Machines à laver": ["washing machine", "machine à laver"],
    "Fours": ["oven", "four de cuisine"],
    "Micro-ondes": ["microwave oven", "micro-ondes"],
    "Climatiseurs": ["air conditioner", "climatiseur split"],
    "Ventilateurs": ["electric fan", "ventilateur"],
    "Petits appareils électroménagers": ["small home appliance", "petit électroménager"],
    "Accessoires électroniques": ["electronic accessory", "accessoire électronique"],
}


def _data_url(uploaded):
    raw = uploaded.read()
    uploaded.seek(0)
    mime = getattr(uploaded, "content_type", None) or mimetypes.guess_type(uploaded.name)[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def _ocr_hint(files):
    """OCR is optional and never required for visual classification."""
    try:
        import pytesseract
        from PIL import Image
        texts = []
        for uploaded in files:
            uploaded.seek(0)
            text = pytesseract.image_to_string(Image.open(uploaded), lang="eng+fra")
            uploaded.seek(0)
            if text.strip():
                texts.append(re.sub(r"\s+", " ", text).strip())
        return " ".join(texts)[:1200]
    except Exception:
        return ""


@lru_cache(maxsize=1)
def _local_model():
    """Load CLIP only when local recognition is requested."""
    from transformers import CLIPModel, CLIPProcessor
    model_name = os.environ.get("UZA_LOCAL_VISION_MODEL", "openai/clip-vit-base-patch32")
    return CLIPProcessor.from_pretrained(model_name), CLIPModel.from_pretrained(model_name)


def _local_analyze(files):
    from PIL import Image
    import torch

    processor, model = _local_model()
    images = []
    for uploaded in files:
        uploaded.seek(0)
        images.append(Image.open(uploaded).convert("RGB"))
        uploaded.seek(0)

    labels = list(CATEGORY_LABELS.keys())
    aggregate = torch.zeros(len(labels), dtype=torch.float32)
    with torch.no_grad():
        for image in images:
            text_inputs = [
                f"a clear photo of a {CATEGORY_LABELS[label][0]}"
                for label in labels
            ]
            inputs = processor(text=text_inputs, images=[image] * len(text_inputs), return_tensors="pt", padding=True)
            outputs = model(**inputs)
            scores = outputs.logits_per_image[0].softmax(dim=0)
            aggregate += scores

    aggregate /= len(images)
    values, indices = torch.topk(aggregate, k=min(5, len(labels)))
    candidates = [
        {"category": labels[int(i)], "confidence": round(float(v) * 100, 1)}
        for v, i in zip(values, indices)
    ]
    best = candidates[0]
    ocr = _ocr_hint(files)
    return {
        "status": "READY",
        "engine": "LOCAL_CLIP",
        "photo_count": 5,
        "object": best["category"],
        "category": best["category"],
        "brand": None,
        "model": None,
        "confidence": best["confidence"],
        "candidates": candidates,
        "evidence": [
            "Silhouette, forme et apparence générale analysées sur les cinq photos.",
            "Les vues multiples ont été combinées pour améliorer la classification.",
        ],
        "ocr_hint": ocr,
        "uncertainty": "La marque et le modèle ne sont pas déclarés sans preuve visuelle suffisante.",
        "message": "Identification locale terminée. Confirmez ou corrigez la catégorie avant de continuer.",
    }


def _openai_analyze(files):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    content = [{"type": "input_text", "text": "Analyse ces cinq photos comme un seul jeu d'images. Identifie l'objet même sans logo, étiquette ou texte en utilisant silhouette, forme, proportions, composants, connecteurs et design. Le texte/OCR est seulement un indice. Ne fabrique jamais une marque ou un modèle. Retourne UNIQUEMENT un JSON avec object, category, brand, model, confidence (0-100), evidence et uncertainty. Si une valeur est indéterminable, mets null."}]
    for uploaded in files:
        content.append({"type": "input_image", "image_url": _data_url(uploaded), "detail": "high"})
    payload = {"model": os.environ.get("UZA_VISION_MODEL", "gpt-5.6-luna"), "input": [{"role": "user", "content": content}]}
    response = requests.post("https://api.openai.com/v1/responses", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json=payload, timeout=90)
    response.raise_for_status()
    data = response.json()
    result = json.loads(data.get("output_text", "").strip())
    result.update(status="READY", engine="OPENAI_FALLBACK", photo_count=5)
    return result


def analyze_images(files):
    if len(files) != 5:
        return {"status": "ERROR", "message": "UZA exige exactement 5 photos.", "photo_count": len(files)}

    mode = os.environ.get("UZA_VISION_MODE", "local").lower()
    fallback = os.environ.get("UZA_VISION_FALLBACK", "none").lower()

    if mode != "openai":
        try:
            result = _local_analyze(files)
            if fallback == "openai" and result.get("confidence", 0) < 55:
                paid = _openai_analyze(files)
                if paid:
                    paid["local_result"] = result
                    return paid
            return result
        except Exception as exc:
            if fallback != "openai":
                return {
                    "status": "LOCAL_UNAVAILABLE",
                    "engine": "LOCAL_CLIP",
                    "confidence": 0,
                    "object": None,
                    "category": None,
                    "brand": None,
                    "model": None,
                    "photo_count": 5,
                    "message": "Le moteur local n'est pas encore installé ou disponible. La publication peut continuer après identification manuelle.",
                    "technical_detail": str(exc),
                }

    try:
        paid = _openai_analyze(files)
        if paid:
            return paid
    except Exception as exc:
        return {"status": "ERROR", "confidence": 0, "photo_count": 5, "message": f"Analyse indisponible : {exc}"}

    return {"status": "LOCAL_UNAVAILABLE", "engine": "LOCAL_CLIP", "confidence": 0, "object": None, "category": None, "brand": None, "model": None, "photo_count": 5, "message": "Aucun moteur de vision disponible. Identifiez l'appareil manuellement pour continuer."}
