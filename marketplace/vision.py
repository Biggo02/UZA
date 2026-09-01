"""UZA product vision engine.

Primary engine: GPT-5.6 Luna vision. Local CLIP remains an offline fallback.
The system can recognize an unlabeled object from shape and appearance, while
never inventing a brand or model that cannot be supported by the images.
"""
import base64
import io
import json
import os
from functools import lru_cache

CATEGORY_LABELS = {
    "Smartphones": ["smartphone", "mobile phone"],
    "Téléphones classiques": ["feature phone", "keypad mobile phone"],
    "Ordinateurs portables": ["laptop", "notebook computer"],
    "Ordinateurs de bureau": ["desktop computer", "desktop PC"],
    "Tablettes": ["tablet computer", "tablet"],
    "Téléviseurs": ["television", "flat screen TV"],
    "Consoles de jeux": ["video game console", "gaming console"],
    "Appareils photo": ["digital camera", "camera"],
    "Caméras": ["video camera", "camcorder"],
    "Audio / enceintes / casques": ["speaker", "headphones", "audio equipment"],
    "Montres connectées": ["smartwatch", "smart watch"],
    "Réfrigérateurs": ["refrigerator", "fridge"],
    "Congélateurs": ["freezer", "chest freezer"],
    "Machines à laver": ["washing machine", "clothes washer"],
    "Fours": ["kitchen oven", "electric oven"],
    "Micro-ondes": ["microwave oven", "microwave"],
    "Climatiseurs": ["air conditioner", "split air conditioner"],
    "Ventilateurs": ["electric fan", "standing fan"],
    "Petits appareils électroménagers": ["small home appliance", "kitchen appliance"],
    "Accessoires électroniques": ["electronic accessory", "computer or phone accessory"],
}

VISION_SYSTEM = """Tu es le moteur de reconnaissance visuelle de la marketplace UZA en RDC.
Tu reçois plusieurs photos du MEME produit, sous plusieurs angles.
Raisonne d'abord sur silhouette, proportions, disposition des composants,
connecteurs, boutons, caméras, écran, charnières, portes, poignées et design.
Un logo, une étiquette ou du texte n'est PAS obligatoire.

Règles:
1. Utilise toutes les vues ensemble comme un seul produit.
2. La catégorie peut être identifiée à partir de la forme même sans marque.
3. Ne donne une marque ou un modèle que si les indices visuels sont suffisants.
4. Ne devine jamais une spécification non visible ou non solidement déductible.
5. Donne des confiances séparées pour catégorie, marque et modèle.
6. Signale les contradictions entre les photos.
7. Retourne uniquement un JSON valide.
"""


def _compressed_data_url(uploaded):
    from PIL import Image, ImageOps
    uploaded.seek(0)
    with Image.open(uploaded) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=82, optimize=True)
    uploaded.seek(0)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def _openai_analyze(files):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    from openai import OpenAI
    client = OpenAI(api_key=key)
    categories = ", ".join(CATEGORY_LABELS.keys())
    prompt = f"""Analyse ces photos comme un seul produit UZA.
Catégories autorisées: {categories}

Retourne exactement un JSON avec:
object, category, category_confidence, brand, brand_confidence, model,
model_confidence, type, visible_attributes, evidence, uncertainty,
photo_consistency.

Les confiances sont de 0 à 100. brand/model = null si non identifiable.
visible_attributes contient uniquement les caractéristiques visibles ou très
solidement déductibles. Adapte les attributs à l'objet reconnu. Pour un
smartphone, examine notamment forme, caméras, écran, boutons, ports et couleur.
Pour un ordinateur, examine charnières, clavier, ports, écran et châssis.
Pour l'électroménager, examine type, portes, poignées, commandes, disposition
et architecture. Ne fabrique jamais une référence ou une capacité.
"""
    content = [{"type": "input_text", "text": prompt}]
    for uploaded in files:
        content.append({"type": "input_image", "image_url": _compressed_data_url(uploaded), "detail": "high"})

    response = client.responses.create(
        model=os.environ.get("UZA_VISION_MODEL", "gpt-5.6-luna"),
        instructions=VISION_SYSTEM,
        input=[{"role": "user", "content": content}],
        max_output_tokens=1800,
    )
    text = (response.output_text or "").strip()
    if text.startswith("```"):
        text = text.replace("```json", "", 1).replace("```", "").strip()
    result = json.loads(text)
    return {
        "status": "READY", "engine": "OPENAI_VISION", "photo_count": len(files),
        "object": result.get("object"), "category": result.get("category"),
        "confidence": result.get("category_confidence", 0),
        "category_confidence": result.get("category_confidence", 0),
        "brand": result.get("brand"), "brand_confidence": result.get("brand_confidence", 0),
        "model": result.get("model"), "model_confidence": result.get("model_confidence", 0),
        "type": result.get("type"), "visible_attributes": result.get("visible_attributes", {}),
        "evidence": result.get("evidence", []), "uncertainty": result.get("uncertainty", []),
        "photo_consistency": result.get("photo_consistency", 0),
        "message": "Analyse visuelle terminée. Vérifiez les informations proposées avant publication.",
    }


@lru_cache(maxsize=1)
def _local_model():
    from transformers import CLIPModel, CLIPProcessor
    name = os.environ.get("UZA_LOCAL_VISION_MODEL", "openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained(name)
    model = CLIPModel.from_pretrained(name)
    model.eval()
    return processor, model


def _read_image(uploaded):
    from PIL import Image
    uploaded.seek(0)
    with Image.open(uploaded) as source:
        source.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
        return source.convert("RGB").copy()


def _local_analyze(files):
    import torch
    processor, model = _local_model()
    labels = list(CATEGORY_LABELS)
    prompts = [f"a clear product photo of {CATEGORY_LABELS[label][0]}" for label in labels]
    aggregate = torch.zeros(len(labels), dtype=torch.float32)
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
    candidates = [{"category": labels[int(i)], "confidence": round(float(v) * 100, 1)} for v, i in zip(values, indices)]
    best = candidates[0]
    return {
        "status": "READY", "engine": "LOCAL_CLIP_FALLBACK", "photo_count": len(files),
        "object": best["category"], "category": best["category"], "confidence": best["confidence"],
        "category_confidence": best["confidence"], "brand": None, "brand_confidence": 0,
        "model": None, "model_confidence": 0, "type": None, "visible_attributes": {},
        "candidates": candidates,
        "evidence": ["Silhouette, forme et apparence générale analysées."],
        "uncertainty": ["Le moteur local ne garantit pas l'identification exacte de la marque ou du modèle."],
        "photo_consistency": 0,
        "message": "Identification locale terminée. Vérifiez la catégorie proposée.",
    }


def analyze_images(files):
    if len(files) != 5:
        return {"status": "ERROR", "message": "UZA exige exactement 5 photos.", "photo_count": len(files)}
    mode = os.environ.get("UZA_VISION_MODE", "openai").lower()
    try:
        if mode != "local":
            result = _openai_analyze(files)
            if result:
                return result
        return _local_analyze(files)
    except Exception as exc:
        if mode != "local":
            try:
                return _local_analyze(files)
            except Exception:
                pass
        return {
            "status": "VISION_UNAVAILABLE", "engine": "NONE", "confidence": 0,
            "category_confidence": 0, "brand": None, "model": None,
            "photo_count": len(files),
            "message": "La reconnaissance automatique est indisponible. Vous pouvez continuer avec une identification manuelle.",
            "technical_detail": str(exc),
        }
