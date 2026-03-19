import re
import unicodedata

# Common tags that appear at the end or within titles that can interfere with matching base games/official entries.
NOISY_TAGS = {
    'esp', 'spa', 'eng', 'usa', 'eur', 'jpn', 'jap', 'ita', 'fra', 'ger',
    'beta', 'demo', 'v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'alpha', 'hack', 
    'translation', 'traducido', 'vers', 'rev', 'fixed', 'patched'
}

def normalize_title(title: str) -> str:
    """
    Normalización simplificada para maximizar la eficacia de difflib.
    """
    if not title:
        return ""
    
    # 1. Bajada a minúsculas y quitar acentos (crítico para difflib)
    t = title.lower()
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode('ascii')
    
    # 2. Sustituir símbolos por espacios (no borrarlos, solo separarlos)
    t = t.replace("_", " ").replace("(", " ").replace(")", " ").replace("[", " ").replace("]", " ").replace("-", " ")
    
    # 3. Eliminar caracteres no alfanuméricos residuales
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    
    # 4. Colapsar espacios y limpiar
    t = re.sub(r'\s+', ' ', t).strip()
    
    return t

def get_search_variations(title: str) -> list[str]:
    """
    Retorna variaciones básicas: la normalizada y la normalizada sin etiquetas ruidosas.
    """
    norm = normalize_title(title)
    if not norm: return []
    
    variations = [norm]
    
    # Versión sin etiquetas comunes (USA, EUR, etc.)
    words = norm.split()
    cleaned_words = [w for w in words if w not in NOISY_TAGS]
    cleaned_norm = " ".join(cleaned_words)
    
    if cleaned_norm and cleaned_norm != norm:
        variations.append(cleaned_norm)
        
    return list(dict.fromkeys(variations))

    # 3. Handle "Title, The" pattern
    if ", the" in title.lower():
        # "Legend of Zelda, The" -> "The Legend of Zelda"
        parts = re.split(r',\s*the', title, flags=re.IGNORECASE)
        if len(parts) > 1:
            alternative = "the " + " ".join(parts)
            variations.append(normalize_title(alternative))
            
    return list(dict.fromkeys(variations)) # Unique values
