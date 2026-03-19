"""
updater.py — Sistema de verificación de actualizaciones de emuladores.

Este módulo consulta la API de GitHub para comparar las versiones instaladas
con las últimas disponibles en sus respectivos repositorios.
"""

import aiohttp
import json
import os
import platform
import re
from typing import Dict, Any, List, Optional

async def check_for_update(github_repo: str, current_version: str) -> dict:
    """
    Consulta la API de GitHub para ver si hay una versión más reciente.
    
    Args:
        github_repo (str): "owner/repo" en GitHub.
        current_version (str): Versión actualmente instalada.
        
    Returns:
        dict: Metadatos sobre la actualización encontrada.
    """
    if not github_repo:
        return {"update_available": False, "latest_version": current_version, "url": ""}

    # Intentar primero con el release oficial 'latest'
    url_latest = f"https://api.github.com/repos/{github_repo}/releases/latest"
    url_all = f"https://api.github.com/repos/{github_repo}/releases"
    headers = {
        "User-Agent": "EmuManager-App",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            # 1. Intentar el endpoint 'latest'
            async with session.get(url_latest, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                elif resp.status == 404:
                    # Si no hay 'latest', intentamos con la lista completa (para repos con pre-releases solo)
                    async with session.get(url_all, timeout=10) as resp_all:
                        if resp_all.status == 200:
                            releases = await resp_all.json()
                            data = releases[0] if releases else None
                        else: data = None
                else: data = None

            if data:
                latest_tag = data.get("tag_name", "").strip()
                html_url = data.get("html_url", "")
                
                # Normalización robusta
                def normalize(v):
                    if not v: return ""
                    v = v.lower().strip()
                    # Quitar prefijos comunes (repetidamente si es necesario)
                    changed = True
                    while changed:
                        changed = False
                        for prefix in ['v', 'build-', 'release-', 'version-', 'preview-', 'latest-']:
                            if v.startswith(prefix):
                                v = v[len(prefix):]
                                changed = True
                    return v

                v_curr_orig = current_version
                v_late_orig = latest_tag

                # Función para comparar versiones de forma numérica y alfanumérica
                def version_is_newer(local, remote):
                    def split_v(v):
                        normalized = normalize(v)
                        # Dividir por puntos, guiones, subrayados
                        return [int(c) if c.isdigit() else c for c in re.split(r'[-._]', normalized) if c]

                    try:
                        l_parts = split_v(local)
                        r_parts = split_v(remote)
                        
                        # Comparar parte por parte
                        for l, r in zip(l_parts, r_parts):
                            if isinstance(l, int) and isinstance(r, int):
                                if r > l: return True
                                if l > r: return False
                            else: # Comparación alfanumérica
                                if str(r) > str(l): return True
                                if str(l) > str(r): return False
                        
                        # Si una versión tiene más partes que la otra, la más larga suele ser más específica/nueva
                        return len(r_parts) > len(l_parts)
                    except Exception as e:
                        logger.warning(f"Error comparando versiones '{local}' y '{remote}': {e}. Fallback a desigualdad.")
                        return remote != local # Fallback a desigualdad si falla el parseo

                v_curr = normalize(v_curr_orig)
                v_late = normalize(v_late_orig)
                
                # Verificación de identidad
                is_same = (v_late == v_curr)
                
                # Caso especial: Hashes de git (comparación parcial)
                if not is_same and len(v_late) >= 7 and len(v_curr) >= 7:
                    if v_late in v_curr or v_curr in v_late:
                        is_same = True

                # Caso especial: Palabras clave (si el usuario instaló una versión "master/rolling")
                # Solo forzamos actualización si la versión local es "detected" (no sabemos qué es)
                # O si la versión remota es un número de versión claro y la local es genérica.
                force_update = False
                if not is_same:
                    if v_curr_orig.lower() in ["detected", "manual"]:
                        force_update = True
                    elif v_curr_orig.lower() == "rolling" and v_late_orig.lower() != "rolling":
                        force_update = True
                
                if force_update:
                    update_available = v_late != ""
                else:
                    # Comparación real de jerarquía para el resto de casos (v1.2 vs v1.3, preview vs latest, etc.)
                    update_available = not is_same and version_is_newer(v_curr_orig, v_late_orig)

                # Log para depuración en consola
                if update_available:
                    print(f"[UPDATER] Actualización disponible para {github_repo}: Local({current_version}) -> Remoto({latest_tag})")
                else:
                    if v_late_orig:
                        print(f"[UPDATER] {github_repo} al día: {latest_tag}")
                
                return {
                    "update_available": update_available,
                    "latest_version": latest_tag,
                    "url": html_url,
                    "release_name": data.get("name", ""),
                    "published_at": data.get("published_at", "")
                }
            else:
                return {
                    "update_available": False, 
                    "latest_version": current_version, 
                    "url": "", 
                    "error": "No data found"
                }
    except Exception as e:
        return {
            "update_available": False, 
            "latest_version": current_version, 
            "url": "", 
            "error": str(e)
        }

async def check_all_updates(installed_emus: dict, available_emus: List[dict]) -> dict:
    """
    Verifica actualizaciones para todos los emuladores instalados actualmente.
    
    Args:
        installed_emus (dict): Datos provenientes de installed.json.
        available_emus (list): Lista de emuladores conocidos (de emulators.json).
        
    Returns:
        dict: Mapa de 'emu_id' -> info de actualización.
    """
    results = {}
    is_win = platform.system() == "Windows"
    
    # Creamos un mapa rápido para buscar el repo correcto según plataforma
    # Nota: Algunos emuladores tienen repos de binarios separados (ej: RPCS3)
    repo_map = {}
    for e in available_emus:
        repo = e.get("github")
        if is_win and e.get("github_win"):
            repo = e.get("github_win")
        elif not is_win and e.get("github_linux"):
            repo = e.get("github_linux")
            
        if repo:
            repo_map[e["id"]] = (repo, e["name"])

    # Iteramos por lo que el usuario tiene realmente instalado
    # El key de installed_emus suele ser el repo principal o ID de repo
    for repo_key, info in installed_emus.items():
        # Intentamos encontrar el emu_id correspondiente en nuestro mapa
        # repo_key en installed.json a veces es "RPCS3/rpcs3"
        emu_id = None
        for eid, (repo, name) in repo_map.items():
            if repo.lower() == repo_key.lower() or name.lower() in repo_key.lower():
                emu_id = eid
                break
        
        if not emu_id:
            continue
            
        current_ver = info.get("version", "")
        repo_to_check, _ = repo_map[emu_id]
        
        update_info = await check_for_update(repo_to_check, current_ver)
        results[emu_id] = update_info
        
    return results
