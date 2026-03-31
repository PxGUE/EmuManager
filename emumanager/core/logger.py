import logging
import sys
import platform
import psutil
from logging.handlers import RotatingFileHandler
from core.config import AppConfig

# --- CONFIGURACIÓN GLOBAL ---
LOG_FORMAT = logging.Formatter(
    '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    datefmt='%H:%M:%S'
)

def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Evitar duplicidad
    if not logger.handlers:
        # 1. Handler para Consola (INFO) - Limpio para desarrollo
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(LOG_FORMAT)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        
        # 2. Handler Profesional con ROTACIÓN (DEBUG) - 5MB x 3 archivos
        log_file = AppConfig.get_app_data_dir() / "logs" / "emumanager.log"
        
        # Asegurar que la carpeta de logs existe antes de abrir el archivo
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(

            log_file, 
            maxBytes=5*1024*1024, # 5MB
            backupCount=3, 
            encoding='utf-8'
        )
        file_handler.setFormatter(LOG_FORMAT)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        
    return logger

# Instancia global principal
EmuLog = setup_logger("EmuManager")

def log_system_info():
    """Registra las specs del sistema al inicio para facilitar el debug."""
    try:
        mem = psutil.virtual_memory()
        cpu_count = psutil.cpu_count(logical=True)
        EmuLog.info("-" * 50)
        EmuLog.info(f"INICIANDO {AppConfig.APP_NAME} (Ecosystem vM.A.N.G.O)")
        EmuLog.info(f"OS: {platform.system()} {platform.release()} ({platform.machine()})")
        EmuLog.info(f"Python: {sys.version.split()[0]}")
        EmuLog.info(f"CPU: {cpu_count} hilos | RAM: {mem.total // (1024**2)}MB")
        EmuLog.info(f"Ruta Datos: {AppConfig.get_app_data_dir()}")
        EmuLog.info("-" * 50)
    except Exception as e:
        EmuLog.warning(f"No se pudo recolectar info del sistema: {e}")

def handle_exception(exc_type, exc_value, exc_traceback):
    """Captura crashes fatales que no pasaron por un try/except."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    EmuLog.critical("¡CRASH FATAL DETECTADO!", exc_info=(exc_type, exc_value, exc_traceback))

# Interceptar excepciones globales
sys.excepthook = handle_exception
