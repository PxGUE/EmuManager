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
    
    # 1.5. Limpiar carpeta de salida anterior para un build limpio
    if os.path.exists(output_dir):
        print(f"Limpiando compilación anterior en: {output_dir}")
        shutil.rmtree(output_dir)
        
    os.makedirs(output_dir)
    
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
        command.insert(6, "--windows-console-mode=disable")
        command.insert(7, "--windows-icon-from-ico=media/icon.ico")

    # 3. Incluir directorios de recursos necesarios
    # IMPORTANTE: NO incluir core/_secrets.py aquí; core se compila automáticamente.
    resources = [
        ("ui/qml", "ui/qml"),
        ("media", "media"), # Solo iconos base, el artwork se descarga
        ("resources", "resources"), # Base de datos de emuladores
    ]
    
    # Comprobar si existen secretos para informar al log
    secrets_path = os.path.join(root_dir, "core", "_secrets.py")
    if os.path.exists(secrets_path):
        print("[BUILD] Secretos encontrados en core/_secrets.py. Serán compilados en el binario.")
    else:
        print("[BUILD] ADVERTENCIA: No se encontró core/_secrets.py. El binario dependerá de variables de entorno.")

    for src, dest in resources:
        full_src = os.path.normpath(os.path.join(root_dir, src))
        # Para directorios usamos --include-data-dir
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
