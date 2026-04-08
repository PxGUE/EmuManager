import pytest
import sqlite3
from pathlib import Path
from backend.database import DatabaseManager

@pytest.fixture
def db_manager(tmp_path):
    db_file = tmp_path / "test_emu.db"
    return DatabaseManager(db_path=db_file)

def test_init_db_creates_tables(db_manager):
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

    assert "scan_paths" in tables
    assert "games" in tables
    assert "game_metadata" in tables
    assert "play_stats" in tables
    assert "emulator_status" in tables

def test_count_all_roms_empty(db_manager):
    assert db_manager.count_all_roms() == 0

def test_insert_and_count_roms(db_manager):
    with db_manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO games (file_hash, file_path, platform, file_size) VALUES (?, ?, ?, ?)",
            ("hash1", "/path/to/game1.sfc", "snes", 1024)
        )
        conn.commit()

    assert db_manager.count_all_roms() == 1

def test_get_all_games(db_manager):
    with db_manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO games (file_hash, file_path, display_name, platform, file_size) VALUES (?, ?, ?, ?, ?)",
            ("hash1", "/path/to/game1.sfc", "Super Mario World", "snes", 1024)
        )
        conn.execute(
            "INSERT INTO game_metadata (game_id, title, is_favorite) VALUES (?, ?, ?)",
            (1, "Super Mario World", 1)
        )
        conn.commit()

    games = db_manager.get_all_games()
    assert len(games) == 1
    assert games[0]["display_name"] == "Super Mario World"
    assert games[0]["is_favorite"] == 1

def test_get_games_by_platform(db_manager):
    with db_manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO games (file_hash, file_path, platform, file_size) VALUES (?, ?, ?, ?)",
            ("hash1", "/path/to/game1.sfc", "snes", 1024)
        )
        conn.execute(
            "INSERT INTO games (file_hash, file_path, platform, file_size) VALUES (?, ?, ?, ?)",
            ("hash2", "/path/to/game2.gb", "gb", 512)
        )
        conn.commit()

    snes_games = db_manager.get_games_by_platform("snes")
    assert len(snes_games) == 1
    assert snes_games[0]["platform"] == "snes"

    gb_games = db_manager.get_games_by_platform("GB") # Test case-insensitivity
    assert len(gb_games) == 1
    assert gb_games[0]["platform"] == "gb"

def test_search_games(db_manager):
    with db_manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO games (file_hash, file_path, display_name, platform, file_size) VALUES (?, ?, ?, ?, ?)",
            ("hash1", "/path/to/zelda.sfc", "The Legend of Zelda", "snes", 1024)
        )
        conn.commit()

    results = db_manager.search_games("Zelda")
    assert len(results) == 1
    assert "Zelda" in results[0]["display_name"]

    results = db_manager.search_games("Mario")
    assert len(results) == 0

def test_get_all_games_limit(db_manager):
    with db_manager.get_connection() as conn:
        for i in range(5):
            conn.execute(
                "INSERT INTO games (file_hash, file_path, platform, file_size) VALUES (?, ?, ?, ?)",
                (f"hash{i}", f"/path/to/game{i}.sfc", "snes", 1024)
            )
        conn.commit()

    games = db_manager.get_all_games(limit=3)
    assert len(games) == 3

def test_update_game_favorite_new_metadata(db_manager):
    with db_manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO games (file_hash, file_path, display_name, platform, file_size) VALUES (?, ?, ?, ?, ?)",
            ("hash1", "/path/to/game1.sfc", "Game 1", "snes", 1024)
        )
        conn.commit()

    db_manager.update_game_favorite(1, True)

    with db_manager.get_connection() as conn:
        row = conn.execute("SELECT is_favorite, title FROM game_metadata WHERE game_id = 1").fetchone()
        assert row["is_favorite"] == 1
        assert row["title"] == "Game 1"

def test_update_game_favorite_existing_metadata(db_manager):
    with db_manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO games (file_hash, file_path, display_name, platform, file_size) VALUES (?, ?, ?, ?, ?)",
            ("hash1", "/path/to/game1.sfc", "Game 1", "snes", 1024)
        )
        conn.execute(
            "INSERT INTO game_metadata (game_id, title, is_favorite) VALUES (?, ?, ?)",
            (1, "Original Title", 0)
        )
        conn.commit()

    db_manager.update_game_favorite(1, True)

    with db_manager.get_connection() as conn:
        row = conn.execute("SELECT is_favorite, title FROM game_metadata WHERE game_id = 1").fetchone()
        assert row["is_favorite"] == 1
        assert row["title"] == "Original Title" # Should not be overwritten by fallback if exists?
        # Actually the code does: ON CONFLICT(game_id) DO UPDATE SET is_favorite = excluded.is_favorite
        # So it only updates is_favorite.

def test_update_game_favorite_non_existent_game(db_manager):
    # Should not raise error
    db_manager.update_game_favorite(999, True)

    with db_manager.get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM game_metadata").fetchone()[0]
        assert count == 0
