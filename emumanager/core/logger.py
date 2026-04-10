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
    
    # IMPORTANTE: Desactivar propagación al root logger para evitar duplicados
    # si otras librerías (como PySide) también inician logs.
    logger.propagate = False
    
    # Limpieza total para evitar duplicidad (especialmente útil en tests)
    if logger.handlers:
        logger.handlers.clear()

    # 1. Handler para Consola (INFO) - Limpio para desarrollo
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(LOG_FORMAT)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # 2. Handler Profesional con ROTACIÓN (Configurable)
    # Ubicación: data/logs/emumanager.log
    log_file = AppConfig.get_app_data_dir() / "logs" / "emumanager.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Nivel según entorno
    file_level = logging.DEBUG if AppConfig.IS_DEV_MODE else logging.INFO

    # Si ya existe un log de una sesión previa, lo rotamos manualmente para empezar frescos
    should_roll = log_file.exists() and log_file.stat().st_size > 0

    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=2*1024*1024, # 2MB (por si acaso una sesión es muy larga)
        backupCount=2,        # 2 respaldos + 1 actual = 3 sesiones totales
        encoding='utf-8'
    )
    
    if should_roll:
        file_handler.doRollover()

    file_handler.setFormatter(LOG_FORMAT)
    file_handler.setLevel(file_level)
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
