import sys
import unittest.mock as mock

mock_qtcore = mock.MagicMock()
def MockSignal(*args, **kwargs):
    s = mock.MagicMock()
    s.emit = mock.MagicMock(name="emit")
    return s
mock_qtcore.Signal = MockSignal

sys.modules['PySide6'] = mock.MagicMock()
sys.modules['PySide6.QtCore'] = mock_qtcore

from PySide6.QtCore import Signal

class X:
    s = Signal(int)

obj = X()
print(f"obj.s: {obj.s}")
print(f"obj.s.emit: {obj.s.emit}")
print(f"type of obj.s.emit: {type(obj.s.emit)}")
print(f"has assert_called: {hasattr(obj.s.emit, 'assert_called')}")
