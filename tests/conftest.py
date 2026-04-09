import sys
import unittest.mock as mock
import tempfile
import shutil
from pathlib import Path

# --- ROBUST GLOBAL MOCKING ---
def setup_qt_mocks():
    # Use a real class for base objects to allow inheritance and attribute access
    class MockIndex:
        def __init__(self, r, c):
            self._r = r
            self._c = c
        def row(self): return self._r
        def column(self): return self._c
        def isValid(self): return True

    class MockQObject:
        def __init__(self, *args, **kwargs): pass
        def moveToThread(self, thread): pass
        def deleteLater(self): pass
        def index(self, row, column, parent=None): return MockIndex(row, column)
        def createIndex(self, row, column, ptr=None): return MockIndex(row, column)
        def beginResetModel(self): pass
        def endResetModel(self): pass

    # Slot decorator that actually returns the function
    def mock_slot(*args, **kwargs):
        if len(args) == 1 and callable(args[0]) and not isinstance(args[0], (type, str)):
            return args[0]
        return lambda f: f

    # Signal descriptor to provide unique mocks per instance
    class MockSignalInstance:
        def __init__(self):
            self.emit = mock.MagicMock(name="emit")
        def connect(self, slot): pass
        def disconnect(self, slot): pass
        def __call__(self, *args, **kwargs): return self

    class MockSignal:
        def __init__(self, *args, **kwargs):
            self._instances = {}
        def __get__(self, instance, owner):
            if instance is None: return self
            if instance not in self._instances:
                self._instances[instance] = MockSignalInstance()
            return self._instances[instance]

    # Pre-add dataChanged to base class
    MockQObject.dataChanged = MockSignal()

    # Create the mock structure
    mock_qt = mock.MagicMock(name="PySide6")
    mock_qt.QtCore.QObject = MockQObject
    mock_qt.QtCore.QAbstractListModel = MockQObject
    mock_qt.QtCore.Signal = MockSignal
    mock_qt.QtCore.Slot = mock_slot
    mock_qt.QtCore.Qt.UserRole = 256
    
    # Property mock that behaves like a real property decorator
    mock_qt.QtCore.Property = lambda *args, **kwargs: property
    
    # CRITICAL: QmlElement decorator must return the class
    mock_qt.QtQml.QmlElement = lambda x: x

    # Register in sys.modules
    sys.modules['PySide6'] = mock_qt
    sys.modules['PySide6.QtCore'] = mock_qt.QtCore
    sys.modules['PySide6.QtWidgets'] = mock_qt.QtWidgets
    sys.modules['PySide6.QtGui'] = mock_qt.QtGui
    sys.modules['PySide6.QtQml'] = mock_qt.QtQml
    sys.modules['PySide6.QtQuick'] = mock_qt.QtQuick

    # Other common dependencies
    for mod in ['psutil', 'pypresence', 'mango_engine']:
        if mod not in sys.modules or isinstance(sys.modules[mod], mock.MagicMock):
            sys.modules[mod] = mock.MagicMock(name=mod)

setup_qt_mocks()

# --- PROJECT PATH SETUP ---
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "emumanager"))

import pytest
import tempfile
import shutil

@pytest.fixture(scope="session", autouse=True)
def test_data_dir():
    """Crea un directorio de datos temporal para toda la sesión de pruebas."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="emumanager_test_"))
    from emumanager.core.config import AppConfig
    AppConfig._custom_data_dir = tmp_dir
    yield tmp_dir
    # Limpieza al finalizar
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)

@pytest.fixture(autouse=True)
def reset_environment(test_data_dir):
    """Reset environment and global mocks between tests."""
    # Reset all known global mocks safely
    for mod in ['psutil', 'pypresence', 'mango_engine']:
        if mod in sys.modules:
            m = sys.modules[mod]
            if hasattr(m, 'reset_mock'):
                m.reset_mock()
                # Also ensure return_value/side_effect are cleared if they were set globally
                if hasattr(m, 'return_value'): m.return_value = mock.DEFAULT
                if hasattr(m, 'side_effect'): m.side_effect = None

    # Reset PySide6 related mocks
    if 'PySide6.QtCore' in sys.modules:
        m = sys.modules['PySide6.QtCore']
        if hasattr(m, 'reset_mock'): m.reset_mock()

    try:
        from emumanager.core.config import AppConfig
        AppConfig._config_cache = None
        AppConfig._app_root = None
    except ImportError:
        pass
    yield
