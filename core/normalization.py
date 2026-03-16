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
    Normalizes a game title for consistent fuzzy matching.
    
    Processing steps:
    1. Replace underscores with spaces.
    2. Remove content in parentheses and brackets (e.g., tags like (USA), [v1.1]).
    3. Convert to lowercase.
    4. Normalize Unicode (NFKD) to handle accents and special characters by decomposition.
    5. Remove non-alphanumeric characters except basic whitespace.
    6. Expand/Normalize Roman Numerals (simple cases like I, II, III, IV, V).
    7. Standardize whitespace.
    """
    if not title:
        return ""
    
    # 1. Underscores to spaces
    t = title.replace("_", " ")
    
    # 2. Open brackets/parentheses to spaces (Preserve content details for matching)
    t = t.replace('(', ' ').replace(')', ' ').replace('[', ' ').replace(']', ' ')
    
    # 3. Lowercase
    t = t.lower()
    
    # 4. Unicode normalization (accents)
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode('ascii')
    
    t = re.sub(r'\bi\b', '1', t)
    t = re.sub(r'\bii\b', '2', t)
    t = re.sub(r'\biii\b', '3', t)
    t = re.sub(r'\biv\b', '4', t)
    t = re.sub(r'\bv\b', '5', t)
    t = re.sub(r'\bvi\b', '6', t)
    t = re.sub(r'\bvii\b', '7', t)
    t = re.sub(r'\bviii\b', '8', t)
    t = re.sub(r'\bix\b', '9', t)
    t = re.sub(r'\bx\b', '10', t)
    t = re.sub(r'\bxi\b', '11', t)
    t = re.sub(r'\bxii\b', '12', t)
    
    # 6. Remove non-alphanumeric
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    
    # 7. Collapse whitespace
    t = re.sub(r'\s+', ' ', t).strip()
    
    return t

def get_search_variations(title: str) -> list[str]:
    """
    Generates variations of a title to increase matching probability.
    E.g., "Legend of Zelda, The" -> ["legend of zelda the", "the legend of zelda"]
    """
    norm = normalize_title(title)
    if not norm:
        return []
    
    variations = [norm]
    
    # 2. Variant without noisy tags (useful for hacks/translations)
    words = norm.split()
    cleaned_words = [w for w in words if w not in NOISY_TAGS]
    if len(cleaned_words) != len(words):
        cleaned_norm = " ".join(cleaned_words)
        if cleaned_norm:
            variations.append(cleaned_norm)

    # 3. Handle "Title, The" pattern
    if ", the" in title.lower():
        # "Legend of Zelda, The" -> "The Legend of Zelda"
        parts = re.split(r',\s*the', title, flags=re.IGNORECASE)
        if len(parts) > 1:
            alternative = "the " + " ".join(parts)
            variations.append(normalize_title(alternative))
            
    return list(dict.fromkeys(variations)) # Unique values
