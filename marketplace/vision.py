import base64
import json
import mimetypes
import os
import requests


def _data_url(uploaded):
    raw = uploaded.read()
    uploaded.seek(0)
    mime = uploaded.content_type or mimetypes.guess_type(uploaded.name)[0] or 'image/jpeg'
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def analyze_images(files):
    if len(files) != 5:
        return {"status": "ERROR", "message": "UZA exige exactement 5 photos."}
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        return {"status": "PENDING_VISION", "confidence": 0, "object": None, "category": None, "brand": None, "model": None, "message": "Moteur de vision non configuré.", "photo_count": 5}
    content = [{"type": "input_text", "text": "Analyse ces cinq photos comme un seul jeu d'images. Identifie l'objet même sans logo, étiquette ou texte en utilisant silhouette, forme, proportions, composants, connecteurs et design. Le texte/OCR est seulement un indice. Ne fabrique jamais une marque ou un modèle. Retourne UNIQUEMENT un JSON avec object, category, brand, model, confidence (0-100), evidence et uncertainty. Si une valeur est indéterminable, mets null."}]
    for f in files:
        content.append({"type": "input_image", "image_url": _data_url(f), "detail": "high"})
    payload = {"model": os.environ.get('UZA_VISION_MODEL', 'gpt-5.6-luna'), "input": [{"role": "user", "content": content}]}
    try:
        r = requests.post('https://api.openai.com/v1/responses', headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}, json=payload, timeout=90)
        r.raise_for_status()
        data = r.json()
        result = json.loads(data.get('output_text', '').strip())
        result.update(status='READY', photo_count=5)
        return result
    except Exception as exc:
        return {"status": "ERROR", "confidence": 0, "object": None, "category": None, "brand": None, "model": None, "message": f"Analyse indisponible : {exc}", "photo_count": 5}
