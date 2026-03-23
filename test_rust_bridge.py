import sys
import os
import time

# Permite cargar la DLL .pyd compilada estando en la carpeta root de EmuManager
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    import core_scanner
    print("✅ Módulo Rust ('core_scanner') importado con éxito:", core_scanner)
    
    start = time.time()
    
    # Pruebe con la carpeta LocalAppData
    test_dir = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    print(f"👉 Escaneando la carpeta gigante: {test_dir} ...")
    
    # extensiones de prueba que busquen base de datos o similares
    results = core_scanner.scan_directory(test_dir, ["db", "sqlite3", "ini"])
    
    end = time.time()
    print(f"⚡ Escaneo finalizado en {end - start:.4f} segundos.")
    print(f"📁 Archivos total encontrados: {len(results)}")
    
    if results:
        print(f"📄 Muestra de los primeros 5: {results[:5]}")
        
except ImportError as e:
    print(f"❌ Error al importar el puente Rust->Python: {e}")
    print("Compila usando: cd core_scanner ; cargo build --release ; Copy-Item target\\release\\core_scanner.dll ..\\core_scanner.pyd")
