import logging
import sys
from pathlib import Path
from core.config import AppConfig

# Configuramos el logger central de EmuManager
log_format = logging.Formatter(
    '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    datefmt='%H:%M:%S'
)

def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Evitar duplicidad si el logger ya existe
    if not logger.handlers:
        # 1. Handler para Consola (Salida estándar)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        
        # 2. Handler para Archivo (En la carpeta data/ de usuario)
        log_file = AppConfig.get_app_data_dir() / "emumanager.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        
    return logger

# Instancia global principal
EmuLog = setup_logger("EmuManager")
