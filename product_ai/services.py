import json
import os
import re
from PIL import Image, ImageEnhance, ImageFilter


def _ocr(image_path):
    try:
        import pytesseract
        image = Image.open(image_path).convert('RGB')
        image = ImageEnhance.Contrast(image).enhance(1.5).filter(ImageFilter.SHARPEN)
        return pytesseract.image_to_string(image, lang=os.getenv('TESSERACT_LANG', 'eng+fra'))
    except Exception:
        return ''

BRANDS = ['Apple','Samsung','Xiaomi','Huawei','Google','OnePlus','Oppo','Vivo','Tecno','Infinix','Nokia','Sony','LG','Lenovo','HP','Dell','Asus','Acer','Microsoft','Canon','Nikon','Philips','Hisense','TCL','Panasonic','Bosch','Whirlpool','Midea','Beko','Haier']
PATTERNS = {
    'Apple': [r'iphone\s*(\d+(?:\s*pro(?:\s*max)?)?)', r'ipad\s*(?:pro|air|mini)?\s*([\w\-]+)?', r'macbook\s*(air|pro)?'],
    'Samsung': [r'galaxy\s+([a-z]\d+[\w\s+\-]*)', r'sm-?[a-z0-9\-]+'],
    'Xiaomi': [r'(redmi\s+[\w\-]+)', r'(mi\s+[\w\-]+)', r'(poco\s+[\w\-]+)'],
    'HP': [r'(elitebook\s+[\w\-]+)', r'(pavilion\s+[\w\-]+)', r'(probook\s+[\w\-]+)'],
    'Lenovo': [r'(thinkpad\s+[\w\-]+)', r'(ideapad\s+[\w\-]+)'],
}


def recognize_product(image_path):
    text = _ocr(image_path)
    normalized = re.sub(r'\s+', ' ', text).strip()
    brand = next((b for b in BRANDS if re.search(r'\b'+re.escape(b)+r'\b', normalized, re.I)), '')
    model = ''
    if brand in PATTERNS:
        for pattern in PATTERNS[brand]:
            match = re.search(pattern, normalized, re.I)
            if match:
                model = match.group(1) if match.groups() else match.group(0)
                break
    category = ''
    low = normalized.lower()
    if re.search(r'iphone|ipad|galaxy|redmi|poco|smartphone|android', low): category = 'Smartphones'
    elif re.search(r'macbook|laptop|notebook|thinkpad|elitebook|pavilion|ideapad', low): category = 'Ordinateurs portables'
    elif re.search(r'tv|television|smart tv|bravia|oled|qled', low): category = 'Téléviseurs'
    elif re.search(r'refrigerator|réfrigérateur|freezer|congelateur', low): category = 'Réfrigérateurs'
    elif re.search(r'washing machine|machine a laver|lave-linge', low): category = 'Machines à laver'
    elif re.search(r'camera|canon|nikon', low): category = 'Appareils photo'
    confidence = 0
    if brand: confidence += 40
    if model: confidence += 40
    if category: confidence += 20
    return {'category': category, 'brand': brand, 'model': model.strip(), 'reference': '', 'text': normalized, 'confidence': confidence}
