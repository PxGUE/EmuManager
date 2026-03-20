import difflib
import re
from typing import Optional, List, TypeVar, Callable
from .normalization import normalize_title, get_search_variations

T = TypeVar('T')

class ScraperEngine:
    """
    Engine de coincidencia unificado para arte y metadatos.
    """
    
    @staticmethod
    def find_best_match(
        target: str, 
        candidates: List[str], 
        min_ratio: float = 0.55,
        require_significant: bool = True
    ) -> Optional[str]:
        """
        Calcula la mejor coincidencia entre un objetivo y múltiples candidatos.
        Prioriza Identidad Exacta -> Inclusión de Tokens -> Ratio de Similitud.
        """
        if not target or not candidates:
            return None
            
        target_norm = normalize_title(target)
        target_tokens = set(target_norm.split())
        # Tokens significativos (más de 2 letras o números)
        sig_target = {t for t in target_tokens if len(t) > 2 or t.isdigit()}
        
        candidate_data = []
        for c in candidates:
            c_norm = normalize_title(c)
            # 1. COINCIDENCIA EXACTA (Tras normalización)
            if target_norm == c_norm:
                return c
            
            c_tokens = set(c_norm.split())
            # 2. IDENTIDAD DE TOKENS (Mismas palabras, distinto orden)
            if target_tokens == c_tokens:
                return c
                
            # 3. INCLUSIÓN (El objetivo es parte integral del candidato o viceversa)
            if sig_target and sig_target.issubset(c_tokens):
                # Caso: "Mario World" -> "Super Mario World"
                candidate_data.append((c, 0.90))
                continue
                
            sig_c = {t for t in c_tokens if len(t) > 2 or t.isdigit()}
            if sig_c and sig_c.issubset(target_tokens):
                # Caso: "Sonic The Hedgehog 2" -> "Sonic 2"
                candidate_data.append((c, 0.85))
                continue

            # 4. DIFflib (Como último recurso para errores tipográficos)
            ratio = difflib.SequenceMatcher(None, target_norm, c_norm).ratio()
            if ratio >= min_ratio:
                candidate_data.append((c, ratio))

        if not candidate_data:
            return None
            
        # Ordenar por el "score" asignado y devolver el mejor
        candidate_data.sort(key=lambda x: x[1], reverse=True)
        return candidate_data[0][0]

    @staticmethod
    def select_best_object(
        target: str,
        objects: List[T],
        key_extractor: Callable[[T], str],
        min_ratio: float = 0.55
    ) -> Optional[T]:
        """
        Selecciona el mejor objeto de una lista basado en una propiedad de texto.
        """
        if not target or not objects:
            return None
            
        # Extraer nombres y mapearlos a objetos
        candidates = []
        obj_map = {}
        for obj in objects:
            name = key_extractor(obj)
            candidates.append(name)
            obj_map[name] = obj
            
        best_name = ScraperEngine.find_best_match(target, candidates, min_ratio)
        return obj_map.get(best_name) if best_name else None
