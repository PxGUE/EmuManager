import sys
from pathlib import Path

def toggle_dev_mode(state: bool):
    config_path = Path(__file__).resolve().parent.parent / "core" / "config.py"
    if not config_path.exists():
        print(f"Error: No se encontró {config_path}")
        sys.exit(1)

    content = config_path.read_text(encoding="utf-8")
    
    if state:
        new_content = content.replace("IS_DEV_MODE = False", "IS_DEV_MODE = True")
        mode_str = "ON (True)"
    else:
        new_content = content.replace("IS_DEV_MODE = True", "IS_DEV_MODE = False")
        mode_str = "OFF (False)"

    if content == new_content:
        print(f"⚠️ El flag IS_DEV_MODE ya estaba en {mode_str} o no se pudo encontrar la línea exacta.")
    else:
        config_path.write_text(new_content, encoding="utf-8")
        print(f"✅ IS_DEV_MODE establecido en {mode_str}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python toggle_dev_mode.py [on|off]")
        sys.exit(1)
    
    target_state = sys.argv[1].lower() == "on"
    toggle_dev_mode(target_state)
