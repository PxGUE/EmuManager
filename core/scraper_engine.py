import difflib
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
        STOP_WORDS = {'the', 'a', 'an', 'of', 'and', 'for', 'with', 'to', 'in', 'on', 'version', 'vol', 'pt', 'part'}
        
        # Filter target words: must be > 2 chars and not a stop word
        significant = {w for w in target_words if len(w) > 2 and w not in STOP_WORDS}
        
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
        min_ratio: float = 0.60,
        require_significant: bool = True
    ) -> Optional[str]:
        """
        Finds the best match for a target string among a list of candidates.
        """
        if not target or not candidates:
            return None
            
        target_variations = get_search_variations(target)
        
        # Normalize candidates once
        candidate_map = {}
        for c in candidates:
            norm = normalize_title(c)
            if norm:
                candidate_map[norm] = c
                
        norm_candidates = list(candidate_map.keys())
        sorted_candidate_map = {ScraperEngine._get_sorted_words(n): n for n in norm_candidates}
        
        best_overall_match = None
        highest_ratio = 0.0
        
        for variant in target_variations:
            # Tier 1: Exact match
            if variant in candidate_map:
                return candidate_map[variant]
                
            # Tier 1.5: Sorted words match (Permutations like 'Ruby Version' / 'Version Ruby')
            sorted_variant = ScraperEngine._get_sorted_words(variant)
            if sorted_variant in sorted_candidate_map:
                return candidate_map[sorted_candidate_map[sorted_variant]]
            
            # Tier 2: get_close_matches (Fast heuristic)
            matches = difflib.get_close_matches(variant, norm_candidates, n=1, cutoff=0.85)
            if matches:
                 # Even with high cutoff, verify significant words (though usually ok)
                if not require_significant or ScraperEngine._check_significant_words(variant, matches[0]):
                    return candidate_map[matches[0]]
            
        # Tier 3: Exhaustive Scan with Significant Word Validation
        for norm_c in norm_candidates:
            ratio = difflib.SequenceMatcher(None, variant, norm_c).ratio()
            
            # If ratio is promising, verify it's not a False Positive (like Pokemon X vs Pokemon Y)
            if ratio > highest_ratio and ratio >= min_ratio:
                if not require_significant or ScraperEngine._check_significant_words(variant, norm_c):
                    highest_ratio = ratio
                    best_overall_match = candidate_map[norm_c]
        
        if best_overall_match:
            return best_overall_match

        # Tier 4: Greedy Fallback (No spaces, no symbols) - For metadata/hacks matching base series
        if not require_significant:
            greedy_highest = 0.0
            greedy_match = None
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
