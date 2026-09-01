from pathlib import Path
import json
import numpy as np

MODEL_NAME = 'openai/clip-vit-base-patch32'


def _model():
    from transformers import CLIPModel, CLIPProcessor
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model = CLIPModel.from_pretrained(MODEL_NAME)
    model.eval()
    return processor, model


def _embedding(processor, model, path):
    from PIL import Image
    import torch
    with Image.open(path) as src:
        src.thumbnail((768, 768), Image.Resampling.LANCZOS)
        image = src.convert('RGB').copy()
    inputs = processor(images=image, return_tensors='pt')
    with torch.inference_mode():
        vector = model.get_image_features(**inputs)
        vector = vector / vector.norm(dim=-1, keepdim=True)
    result = vector[0].detach().cpu().numpy().astype('float32')
    del inputs, vector, image
    return result


def build_index(rows, index_dir, rebuild=False):
    index_dir = Path(index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)
    meta_path = index_dir / 'metadata.json'
    index_path = index_dir / 'index.faiss'
    if not rows:
        meta_path.write_text('[]', encoding='utf-8')
        return {'vectors': 0, 'references': 0, 'file': str(index_path)}
    processor, model = _model()
    vectors, metadata = [], []
    for row in rows:
        try:
            vectors.append(_embedding(processor, model, row['image_path']))
            metadata.append(row)
        except Exception:
            continue
    if not vectors:
        raise RuntimeError('Aucune image valide pour construire l’index.')
    matrix = np.stack(vectors).astype('float32')
    try:
        import faiss
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        faiss.write_index(index, str(index_path))
    except ImportError:
        np.save(index_dir / 'index.npy', matrix)
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding='utf-8')
    references = len({(m['listing_id'], m['brand'], m['model']) for m in metadata})
    return {'vectors': len(metadata), 'references': references, 'file': str(index_path)}


def search_index(image_paths, index_dir, top_k=20):
    index_dir = Path(index_dir)
    metadata = json.loads((index_dir / 'metadata.json').read_text(encoding='utf-8'))
    if not metadata:
        return []
    processor, model = _model()
    query_vectors = np.stack([_embedding(processor, model, p) for p in image_paths]).astype('float32')
    try:
        import faiss
        index = faiss.read_index(str(index_dir / 'index.faiss'))
        scores, ids = index.search(query_vectors, min(top_k, len(metadata)))
    except (ImportError, RuntimeError, FileNotFoundError):
        matrix = np.load(index_dir / 'index.npy')
        scores = query_vectors @ matrix.T
        ids = np.argsort(-scores, axis=1)[:, :min(top_k, len(metadata))]
        scores = np.take_along_axis(scores, ids, axis=1)
    grouped = {}
    for row_scores, row_ids in zip(scores, ids):
        for score, idx in zip(row_scores, row_ids):
            if idx < 0:
                continue
            item = metadata[int(idx)]
            key = (item['listing_id'], item['brand'], item['model'])
            grouped.setdefault(key, {'listing_id': item['listing_id'], 'brand': item['brand'], 'model': item['model'], 'category': item['category'], 'matches': []})
            grouped[key]['matches'].append(float(score))
    results = []
    for item in grouped.values():
        best = sorted(item['matches'], reverse=True)[:min(3, len(item['matches']))]
        item['score'] = round(float(np.mean(best)) * 100, 1)
        del item['matches']
        results.append(item)
    return sorted(results, key=lambda x: x['score'], reverse=True)[:10]
