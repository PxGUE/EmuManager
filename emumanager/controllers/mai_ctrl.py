import os
import requests
from pathlib import Path
from PySide6.QtCore import QObject, Slot, Signal, QThread, Property
from core.config import AppConfig
from core.logger import EmuLog
from llama_cpp import Llama

class MAIDownloadWorker(QObject):
    progress = Signal(float)
    status = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, target_path, url):
        super().__init__()
        self.target_path = target_path
        self.url = url
        self._is_cancelled = False

    def run(self):
        try:
            self.status.emit("connecting")
            response = requests.get(self.url, stream=True, timeout=15)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._is_cancelled:
                        f.close()
                        if os.path.exists(self.target_path):
                            os.remove(self.target_path)
                        self.finished.emit(False, "download_cancelled")
                        return
                        
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.progress.emit(downloaded / total_size)
            
            self.finished.emit(True, "download_success")
        except Exception as e:
            EmuLog.error(f"M.A.I (Downloader): Error crítico: {e}")
            self.finished.emit(False, str(e))

class MAIController(QObject):
    """
    Controlador para el ecosistema M.A.I (Mango AI).
    Gestiona el ciclo de vida del modelo local (SmolLM2-135M).
    """
    statusChanged = Signal(str)
    modelReadyChanged = Signal()
    downloadProgressChanged = Signal()
    
    REPO_ID = "Paidex/mai_pocket"
    MODEL_FILENAME = "MAI_pocket.gguf"
    MODEL_URL = f"https://huggingface.co/{REPO_ID}/resolve/main/{MODEL_FILENAME}"

    def __init__(self, main_controller=None):
        super().__init__(main_controller)
        self.main_ctrl = main_controller
        self._download_thread = None
        self._download_worker = None
        self._is_downloading = False
        self._model_path = self._get_model_path()
        self._llm = None
        self._status = "ready" if self.isReady else "not_installed"
        self._download_progress = 0.0

    @Property(bool, notify=modelReadyChanged)
    def isReady(self):
        """Indica si el modelo GGUF existe localmente."""
        return self._model_path.exists()

    @Property(bool, notify=statusChanged)
    def isDownloading(self):
        return self._is_downloading

    @Property(str, notify=statusChanged)
    def status(self):
        return self._status

    @Property(float, notify=downloadProgressChanged)
    def downloadProgress(self):
        return self._download_progress

    def _get_model_path(self):
        """Retorna la ruta absoluta al modelo en AppData."""
        models_dir = AppConfig.get_app_data_dir() / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        return models_dir / self.MODEL_FILENAME

    @Slot()
    def start_download(self):
        """Inicia la descarga asíncrona del modelo especialista."""
        if self._is_downloading or self.isReady:
            return

        target = self._get_model_path()
        self._is_downloading = True
        self._status = "downloading"
        self.statusChanged.emit(self._status)

        self._download_thread = QThread()
        self._download_worker = MAIDownloadWorker(target, self.MODEL_URL)
        self._download_worker.moveToThread(self._download_thread)

        self._download_worker.progress.connect(self._on_download_progress_internal)
        self._download_worker.status.connect(self._on_download_status_internal)
        self._download_worker.finished.connect(self._on_download_finished)
        
        self._download_thread.started.connect(self._download_worker.run)
        self._download_thread.start()

        EmuLog.info("M.A.I: Iniciando descarga del motor inteligente desde HuggingFace...")

    def _on_download_progress_internal(self, p):
        self._download_progress = p
        self.downloadProgressChanged.emit()

    def _on_download_status_internal(self, s):
        self._status = s
        self.statusChanged.emit(s)

    def _on_download_finished(self, success, msg):
        self._is_downloading = False
        self._download_thread.quit()
        self._download_thread.wait()
        
        if success:
            self._status = "ready"
            self._download_progress = 1.0
            EmuLog.info("M.A.I: Motor inteligente instalado y listo para la acción.")
            if self.main_ctrl:
                self.main_ctrl.notificationRequested.emit(
                    "M.A.I Online",
                    "mai_installed_success",
                    "success"
                )
        else:
            self._status = "error"
            EmuLog.error(f"M.A.I: Fallo en instalación: {msg}")
            if self.main_ctrl:
                self.main_ctrl.notificationRequested.emit(
                    "M.A.I Error",
                    f"mai_installed_error|{msg}",
                    "error"
                )
        
        self.statusChanged.emit(self._status)
        self.modelReadyChanged.emit()

    @Slot()
    def uninstall_model(self):
        """Elimina el modelo local para liberar espacio."""
        target = self._get_model_path()
        if target.exists():
            try:
                if self._llm:
                    self._llm = None # Liberar RAM
                os.remove(target)
                self._status = "not_installed"
                self.statusChanged.emit(self._status)
                self.modelReadyChanged.emit()
                EmuLog.info("M.A.I: Motor desinstalado localmente.")
            except Exception as e:
                EmuLog.error(f"M.A.I: Error al desinstalar: {e}")

    # --- MOTOR DE INFERENCIA (NÚCLEO M.A.I) ---

    def _ensure_loaded(self):
        """Carga el modelo en RAM solo cuando se solicita su uso."""
        if self._llm:
            return True
        
        if not self.isReady:
            EmuLog.error("M.A.I: Intento de uso sin modelo instalado.")
            return False

        try:
            EmuLog.info(f"M.A.I: Cargando inteligencia local ({self.MODEL_FILENAME})...")
            self._llm = Llama(
                model_path=str(self._get_model_path()),
                n_ctx=2048,
                n_threads=4,
                verbose=False
            )
            return True
        except Exception as e:
            EmuLog.error(f"M.A.I (Inference): Error al cargar: {e}")
            return False

    @Slot(str, result=str)
    def extract_metadata(self, raw_text):
        """
        Recibe texto crudo de Wikipedia y lo transforma en JSON estructurado.
        Este es el método que usará Mango Scraper.
        """
        if not self._ensure_loaded():
            return ""

        # Usamos el exacto mismo prompt alpaca del entrenamiento
        prompt = f"### Analiza este texto y extrae metadatos JSON:\n{raw_text[:1500]}\n\n### JSON:\n"

        try:
            # Inferencia local (Puro poder local-first)
            response = self._llm(
                prompt,
                max_tokens=300,
                temperature=0.1, # Creatividad mínima para evitar errores
                stop=["###", "}"],
                echo=False
            )
            
            output = response["choices"][0]["text"].strip()
            
            # Autocierre de JSON si el modelo fue demasiado tímido
            if not output.endswith("}"):
                output += "}"
                
            return output
            
        except Exception as e:
            EmuLog.error(f"M.A.I (Extraction): Error en proceso: {e}")
            return ""
