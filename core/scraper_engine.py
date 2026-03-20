import difflib
import re
from typing import Optional, List, TypeVar, Callable
from .normalization import normalize_title, get_search_variations

T = TypeVar('T')

class ScraperEngine:
    """
    Unified fuzzy matching engine for artwork and metadata.
    """
    
    @staticmethod
    def _get_sorted_words(text: str) -> str:
        """Returns sorted words for order-independent comparison."""
        words = text.split()
        words.sort()
        return " ".join(words)

    @staticmethod
    def _check_significant_words(target_norm: str, candidate_norm: str) -> bool:
        """
        Ensures that significant words in the target are present in the candidate.
        Helps distinguish between 'Pokemon Ruby' and 'Pokemon Sapphire'.
        """
        target_words = set(target_norm.split())
        candidate_words = set(candidate_norm.split())
        
        # Stop words that don't count as "significant" for distinguishing games
        STOP_WORDS = {
            'the', 'a', 'an', 'of', 'and', 'for', 'with', 'to', 'in', 'on', 'version', 'vol', 'pt', 'part',
            'usa', 'eur', 'jpn', 'esp', 'spa', 'fra', 'ger', 'ita', 'hack', 'beta', 'demo', 'rev', 'v0', 'v1', 'v2',
            'juego', 'videojuego', 'game', 'video'
        }
        
        # Filter target words: must be > 2 chars OR be a digit OR be a short Roman Numeral
        significant = {w for w in target_words if ((len(w) > 2 or w.isdigit()) and w not in STOP_WORDS)}
        
        if not significant:
            return True # If no significant words (weird), allow fuzzy match
            
        # Check how many significant target words are in the candidate
        # For precision, we want most of them to be there.
        # But some might be hyphenated or slightly different if normalization varied.
        found_count = 0
        for sig in significant:
            if sig in candidate_words:
                found_count += 1
            else:
                # Check for partial matches or minor spelling differences (fuzzy containment)
                for cw in candidate_words:
                    if len(cw) > 2 and (sig in cw or cw in sig):
                        found_count += 1
                        break
        
        # We require at least 80% of significant words to be present
        return (found_count / len(significant)) >= 0.80

    @staticmethod
    def find_best_match(
        target: str, 
        candidates: List[str], 
        min_ratio: float = 0.55,
        require_significant: bool = True
    ) -> Optional[str]:
        """
        Calcula la mejor coincidencia entre un objetivo y múltiples candidatos.
        Utiliza una estrategia multi-etapa: Exacto -> Permutado -> Heurístico -> Exhaustivo.
        """
        if not target or not candidates:
            return None
            
        target_variations = get_search_variations(target)
        
        # 1. Preparar mapa de candidatos normalizados
        candidate_map = {}
        for c in candidates:
            norm = normalize_title(c)
            if norm:
                candidate_map[norm] = c
                
        norm_candidates = list(candidate_map.keys())
        sorted_candidate_map = {ScraperEngine._get_sorted_words(n): n for n in norm_candidates}
        
        best_overall_match = None
        highest_ratio = 0.0

        # ETAPAS 1 y 2: Búsquedas rápidas (Exactas y Heurística de difflib)
        for variant in target_variations:
            if variant in candidate_map:
                return candidate_map[variant]
                
            sorted_variant = ScraperEngine._get_sorted_words(variant)
            if sorted_variant in sorted_candidate_map:
                return candidate_map[sorted_candidate_map[sorted_variant]]
            
            matches = difflib.get_close_matches(variant, norm_candidates, n=1, cutoff=0.85)
            if matches:
                if not require_significant or ScraperEngine._check_significant_words(variant, matches[0]):
                    return candidate_map[matches[0]]

        # ETAPA 3: Escaneo Exhaustivo con todas las variaciones
        # Esto permite que Tony Hawk's (USA) coincida con Tony Hawk's sin tags.
        for variant in target_variations:
            for norm_c in norm_candidates:
                v_words = set(variant.split())
                c_words = set(norm_c.split())
                
                # Coincidencia por sub-conjunto (Muy potente para nombres largos)
                if v_words and v_words.issubset(c_words):
                    ratio = 0.95
                elif c_words.issubset(v_words):
                    ratio = 0.90
                else:
                    ratio = difflib.SequenceMatcher(None, variant, norm_c).ratio()
                
                if ratio > highest_ratio:
                    if not require_significant or ScraperEngine._check_significant_words(variant, norm_c):
                        highest_ratio = ratio
                        best_overall_match = candidate_map[norm_c]
                        # Si encontramos una coincidencia casi perfecta, paramos
                        if ratio >= 0.98: return best_overall_match

        if best_overall_match and highest_ratio >= min_ratio:
            return best_overall_match

        # ETAPA 4: Fallback "Greedy" (Sin espacios ni símbolos)
        if not require_significant:
            greedy_highest = 0.0
            greedy_match = None
            for variant in target_variations:
                v_greedy = re.sub(r'[^a-z0-9]', '', variant)
                for norm_c in norm_candidates:
                    c_greedy = re.sub(r'[^a-z0-9]', '', norm_c)
                    ratio = difflib.SequenceMatcher(None, v_greedy, c_greedy).ratio()
                    if ratio > greedy_highest and ratio >= min_ratio:
                        greedy_highest = ratio
                        greedy_match = candidate_map[norm_c]
            return greedy_match
                    
        return None

    @staticmethod
    def select_best_object(
        target: str,
        objects: List[T],
        key_extractor: Callable[[T], str],
        min_ratio: float = 0.55
    ) -> Optional[T]:
        """
        Selects the best object from a list based on a string property.
        """
        if not target or not objects:
            return None
            
        # Extract names and map them to objects
        candidates = []
        obj_map = {}
        for obj in objects:
            name = key_extractor(obj)
            candidates.append(name)
            obj_map[name] = obj
            
        best_name = ScraperEngine.find_best_match(target, candidates, min_ratio)
        return obj_map.get(best_name) if best_name else None
