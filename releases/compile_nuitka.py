import os
import sys
import subprocess
import shutil

#Comando para crear el ejecutable: python releases/compile_nuitka.py

def compile():
    print("--- EmuManager Compilation with Nuitka ---")
    
    # 1. Rutas base
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    main_py = os.path.join(root_dir, "main.py")
    output_dir = os.path.join(root_dir, "releases", "build_output")
    
    # 2. Comando base de Nuitka
    command = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--enable-plugin=pyside6",
        "--include-qt-plugins=qml",
        f"--output-dir={output_dir}",
        "--output-filename=emumanager",
        "--remove-output", # Limpia la carpeta de build temporal al terminar
        main_py
    ]

    # Flags específicos de Windows
    if sys.platform == "win32":
        command.insert(6, "--windows-disable-console")
        # command.insert(7, "--windows-icon-from-ico=media/logo.ico")

    # 3. Incluir directorios de recursos necesarios
    # Nuitka copiará estos directorios dentro del paquete
    resources = [
        ("ui/qml", "ui/qml"),
        ("media", "media"), # Solo iconos base, el artwork se descarga
        ("resources", "resources"), # Base de datos de emuladores
    ]
    
    for src, dest in resources:
        full_src = os.path.normpath(os.path.join(root_dir, src))
        command.append(f"--include-data-dir={full_src}={dest}")

    print(f"Ejecutando comando: {' '.join(command)}")
    
    try:
        subprocess.run(command, check=True)
        print("\n[OK] Compilación finalizada en releases/")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] El proceso falló: {e}")
    except Exception as e:
        print(f"\n[ERROR] Ocurrió algo inesperado: {e}")

if __name__ == "__main__":
    compile()
