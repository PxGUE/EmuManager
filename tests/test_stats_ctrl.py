import sys
import os
from unittest.mock import MagicMock, patch

# Mock PySide6 before it is imported in the controller
class MockQObject:
    def __init__(self, parent=None, **kwargs):
        pass

mock_qtcore = MagicMock()
mock_qtcore.QObject = MockQObject
mock_qtcore.Slot = lambda *args, **kwargs: lambda func: func
mock_qtcore.Signal = lambda *args, **kwargs: MagicMock()

sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = mock_qtcore

# Mock other potential dependencies if needed
sys.modules['pypresence'] = MagicMock()
sys.modules['psutil'] = MagicMock()

import pytest
from pathlib import Path

# Add emumanager to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from emumanager.controllers.stats_ctrl import StatsController
from emumanager.backend.database import DatabaseManager

@pytest.fixture
def db_manager(tmp_path):
    # Use a temporary file for the database to persist across connections
    db_file = tmp_path / "test_emu.db"
    db = DatabaseManager(db_path=db_file)
    return db

@pytest.fixture
def stats_ctrl(db_manager):
    return StatsController(db=db_manager)

def test_get_games_count(stats_ctrl, db_manager):
    # Setup: Insert some games
    with db_manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO games (file_hash, file_path, platform, file_size) VALUES (?, ?, ?, ?)",
            ("hash1", "/path/to/game1.sfc", "snes", 1024)
        )
        conn.execute(
            "INSERT INTO games (file_hash, file_path, platform, file_size) VALUES (?, ?, ?, ?)",
            ("hash2", "/path/to/game2.nes", "nes", 2048)
        )
        conn.commit()

    # Test
    assert stats_ctrl.get_games_count() == 2

    # Test caching (DatabaseManager has internal cache)
    with db_manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO games (file_hash, file_path, platform, file_size) VALUES (?, ?, ?, ?)",
            ("hash3", "/path/to/game3.gba", "gba", 512)
        )
        conn.commit()

    # Should still be 2 due to cache
    assert stats_ctrl.get_games_count() == 2

    # Clear cache
    stats_ctrl.clear_cache()
    assert stats_ctrl.get_games_count() == 3

def test_get_system_info_success(stats_ctrl):
    with patch.dict('sys.modules', {'mango_engine': MagicMock()}):
        info = stats_ctrl.get_system_info()
        assert info["is_engine_ready"] is True
        assert "app_name" in info
        assert "os" in info

def test_get_system_info_no_engine(stats_ctrl):
    with patch.dict('sys.modules', {'mango_engine': None}):
        # When sys.modules['mango_engine'] is None, importing it raises ImportError
        # But we need to make sure the import actually happens in the method.
        # stats_ctrl.py does 'import mango_engine' inside get_system_info
        with patch('builtins.__import__', side_effect=ImportError):
            info = stats_ctrl.get_system_info()
            assert info["is_engine_ready"] is False

def test_get_consoles_summary_caching(stats_ctrl):
    mock_mango = MagicMock()
    mock_mango.fetch_consoles_summary.return_value = [
        {"platform": "snes", "gameCount": 10, "playTime": 3600, "hasCore": True, "emulatorName": "Snes9x"}
    ]

    with patch.dict('sys.modules', {'mango_engine': mock_mango}):
        # First call
        res1 = stats_ctrl.get_consoles_summary()
        assert len(res1) == 1
        assert res1[0]["platform"] == "snes"
        assert res1[0]["title"] == "SNES"

        # Modify mock return to see if cache is used
        mock_mango.fetch_consoles_summary.return_value = []
        res2 = stats_ctrl.get_consoles_summary(use_cache=True)
        assert len(res2) == 1 # Still returns cached data

        # Call with use_cache=False
        res3 = stats_ctrl.get_consoles_summary(use_cache=False)
        assert len(res3) == 0

        # Verify cache update
        mock_mango.fetch_consoles_summary.return_value = [
            {"platform": "nes", "gameCount": 5, "playTime": 1800, "hasCore": True, "emulatorName": "Nestopia"}
        ]
        res4 = stats_ctrl.get_consoles_summary(use_cache=False)
        assert len(res4) == 1
        assert res4[0]["platform"] == "nes"

def test_get_dashboard_stats_mapping(stats_ctrl, db_manager):
    # Setup Database
    with db_manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO games (id, file_hash, file_path, display_name, platform, file_size) VALUES (?, ?, ?, ?, ?, ?)",
            (1, "h1", "/p1", "Super Mario", "snes", 100)
        )
        conn.execute(
            "INSERT INTO games (id, file_hash, file_path, display_name, platform, file_size) VALUES (?, ?, ?, ?, ?, ?)",
            (2, "h2", "/p2", "Zelda", "nes", 200)
        )
        conn.commit()

    mock_mango = MagicMock()
    mock_mango.fetch_dashboard_stats.return_value = {
        "total_games": 2,
        "last_game": {"id": 1},
        "recent_games": [{"id": 2}, {"id": 3}] # 3 doesn't exist
    }

    with patch.dict('sys.modules', {'mango_engine': mock_mango}):
        stats = stats_ctrl.get_dashboard_stats()

        assert stats["total_games"] == 2
        assert stats["last_game"]["title"] == "Super Mario"
        assert stats["recent_games"][0]["title"] == "Zelda"
        # ID 3 is missing in DB, so it shouldn't have a title or should be handled gracefully
        assert "title" not in stats["recent_games"][1]

def test_get_dashboard_stats_empty_engine_result(stats_ctrl):
    mock_mango = MagicMock()
    mock_mango.fetch_dashboard_stats.return_value = {}

    with patch.dict('sys.modules', {'mango_engine': mock_mango}):
        stats = stats_ctrl.get_dashboard_stats()
        assert stats == {}

def test_get_dashboard_stats_engine_none(stats_ctrl):
    mock_mango = MagicMock()
    mock_mango.fetch_dashboard_stats.return_value = None

    with patch.dict('sys.modules', {'mango_engine': mock_mango}):
        stats = stats_ctrl.get_dashboard_stats()
        assert stats == {}

def test_get_dashboard_stats_import_error(stats_ctrl):
    with patch('builtins.__import__', side_effect=ImportError):
        stats = stats_ctrl.get_dashboard_stats()
        assert stats == {}

def test_get_consoles_summary_unknown_platform(stats_ctrl):
    mock_mango = MagicMock()
    mock_mango.fetch_consoles_summary.return_value = [
        {"platform": "imaginary_console", "gameCount": 1, "playTime": 0, "hasCore": False, "emulatorName": ""}
    ]

    with patch.dict('sys.modules', {'mango_engine': mock_mango}):
        res = stats_ctrl.get_consoles_summary(use_cache=False)
        assert len(res) == 1
        assert res[0]["platform"] == "imaginary_console"
        assert res[0]["title"] == "OTROS" # Fallback
        assert res[0]["iconEmoji"] == "❓"
