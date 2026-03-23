import core_scanner
import time
from pathlib import Path

def test_scan():
    # Usar el directorio actual para la prueba
    test_path = str(Path.cwd())
    print(f"--- Iniciando Escaneo de Prueba en: {test_path} ---")
    
    start_time = time.time()
    # Escanear archivos .py y .qml (que sabemos que existen aquí)
    results = core_scanner.scan_directory(test_path, ["py", "qml", "rs"])
    end_time = time.time()
    
    print(f"Escaneo completado en {end_time - start_time:.4f} segundos")
    print(f"Archivos encontrados: {len(results)}")
    
    if results:
        print("\nEjemplo de primer archivo encontrado:")
        first = results[0]
        print(f"  Ruta: {first['path']}")
        print(f"  MD5:  {first['md5']}")
        print(f"  CRC32: {first['crc32']}")
        print(f"  Tamaño: {first['size']} bytes")

if __name__ == "__main__":
    try:
        test_scan()
    except Exception as e:
        print(f"ERROR durante la prueba: {e}")
