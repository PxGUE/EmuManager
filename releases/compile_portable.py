import os
import sys
import subprocess
import shutil

# Comando para crear la versión portable (un solo archivo): python releases/compile_portable.py

def compile_portable():
    print("--- EmuManager Portable Compilation (OneFile) with Nuitka ---")
    
    # 1. Rutas base
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main_py = os.path.join(root_dir, "main.py")
    output_dir = os.path.join(root_dir, "releases", "portable")
    
    # 1.5. Limpiando para un build limpio
    if os.path.exists(output_dir):
        print(f"Limpiando compilación portable anterior en: {output_dir}")
        shutil.rmtree(output_dir)
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 2. Comando base de Nuitka
    command = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile", # Esta es la clave para la versión portable
        "--enable-plugin=pyside6",
        "--include-qt-plugins=qml",
        f"--output-dir={output_dir}",
        "--output-filename=emumanager_portable",
        "--remove-output",
        main_py
    ]

    # Flags específicos de Windows
    if sys.platform == "win32":
        command.append("--windows-console-mode=disable")
        command.append("--windows-icon-from-ico=media/icon.ico")

    # 3. Incluir directorios de recursos necesarios
    resources = [
        ("ui/qml", "ui/qml"),
        ("media", "media"),
        ("resources", "resources"),
    ]
    
    for src, dest in resources:
        full_src = os.path.normpath(os.path.join(root_dir, src))
        # En modo onefile, Nuitka agrupa todo dentro del ejecutable
        command.append(f"--include-data-dir={full_src}={dest}")

    print(f"Ejecutando comando: {' '.join(command)}")
    
    try:
        subprocess.run(command, check=True)
        print(f"\n[OK] Versión portable finalizada en {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] El proceso falló: {e}")
    except Exception as e:
        print(f"\n[ERROR] Ocurrió algo inesperado: {e}")

if __name__ == "__main__":
    compile_portable()
