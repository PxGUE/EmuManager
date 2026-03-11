import difflib
from typing import Optional, List, TypeVar, Callable
from .normalization import normalize_title, get_search_variations

T = TypeVar('T')

class ScraperEngine:
    """
    Unified fuzzy matching engine for artwork and metadata.
    """
    
    @staticmethod
    def find_best_match(
        target: str, 
        candidates: List[str], 
        min_ratio: float = 0.60
    ) -> Optional[str]:
        """
        Finds the best match for a target string among a list of candidates.
        Uses a multi-tier strategy:
        1. Exact normalized match.
        2. get_close_matches (high threshold).
        3. Full SequenceMatcher ratio scan.
        """
        if not target or not candidates:
            return None
            
        target_variations = get_search_variations(target)
        
        # Prepare candidate map: normalized -> original
        # We cache this if we do multiple searches on the same candidates list?
        # For simplicity now, we rebuild it.
        candidate_map = {normalize_title(c): c for c in candidates}
        norm_candidates = list(candidate_map.keys())
        
        best_overall_match = None
        highest_ratio = 0.0
        
        for variant in target_variations:
            # 1. Tier 1: Exact match
            if variant in candidate_map:
                return candidate_map[variant]
                
            # 2. Tier 2: get_close_matches (Fast heuristic)
            matches = difflib.get_close_matches(variant, norm_candidates, n=1, cutoff=0.85)
            if matches:
                return candidate_map[matches[0]]
            
            # 3. Tier 3: Exhaustive Scan
            for norm_c in norm_candidates:
                ratio = difflib.SequenceMatcher(None, variant, norm_c).ratio()
                if ratio > highest_ratio:
                    highest_ratio = ratio
                    best_overall_match = candidate_map[norm_c]
                    
        if highest_ratio >= min_ratio:
            return best_overall_match
            
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
        Uses title variations for target.
        """
        if not target or not objects:
            return None
            
        target_variations = get_search_variations(target)
        best_obj = None
        highest_overall_ratio = 0.0
        
        for variant in target_variations:
            for obj in objects:
                obj_name = key_extractor(obj)
                obj_norm = normalize_title(obj_name)
                
                if variant == obj_norm:
                    return obj
                    
                ratio = difflib.SequenceMatcher(None, variant, obj_norm).ratio()
                if ratio > highest_overall_ratio:
                    highest_overall_ratio = ratio
                    best_obj = obj
                
        if highest_overall_ratio >= min_ratio:
            return best_obj
            
        return None
