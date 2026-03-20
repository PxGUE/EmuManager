import re
import unicodedata

# Extended noisy tags to cover more common scene and region identifiers
NOISY_TAGS = {
    'esp', 'spa', 'eng', 'usa', 'eur', 'jpn', 'jap', 'ita', 'fra', 'ger',
    'beta', 'demo', 'v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'alpha', 'hack', 
    'translation', 'traducido', 'vers', 'rev', 'fixed', 'patched', 'clone',
    'pal', 'ntsc', 'unlicensed', 'proto', 'hidden', 'fixed'
}

def normalize_title(title: str) -> str:
    """
    Normalización orientada a maximizar la eficacia de difflib y ScreenScraper.
    """
    if not title:
        return ""
    
    # 1. Quitar contenido entre paréntesis y corchetes (Suele ser basura: [!], (USA), etc)
    t = re.sub(r'[\(\[].*?[\)\]]', ' ', title)
    
    # 2. Lowercase y quitar acentos
    t = t.lower()
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode('ascii')
    
    # 3. Sustituir símbolos por espacios
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    
    # 4. Colapsar espacios y limpiar
    t = re.sub(r'\s+', ' ', t).strip()
    
    return t

def get_search_variations(title: str) -> list:
    """
    Genera variaciones de búsqueda inteligentes.
    """
    # 1. El nombre tal cual (normalizado)
    norm = normalize_title(title)
    if not norm: return []
    
    variations = [norm]
    
    # 2. Sin tags ruidosos
    cleaned_words = [w for w in norm.split() if w not in NOISY_TAGS]
    cleaned = " ".join(cleaned_words)
    if cleaned and cleaned != norm:
        variations.append(cleaned)
        
    # 3. Solo la primera parte (antes del primer sep fuerte como ":" o "-")
    # Ejemplo: "Sonic Adventure 2: Battle" -> "Sonic Adventure 2"
    if ":" in title or "-" in title:
        base = re.split(r'[:\-]', title)[0]
        base_norm = normalize_title(base)
        if base_norm and base_norm not in variations:
            variations.append(base_norm)
            
    return list(dict.fromkeys(variations))
