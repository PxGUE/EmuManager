import os
import sys
import sqlite3
import pytest
from pathlib import Path

# Add emumanager to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "emumanager"))

from backend.database import DatabaseManager

def test_database_initialization(tmp_path):
    db_file = tmp_path / "test_emu.db"
    db_manager = DatabaseManager(db_path=db_file)

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ["scan_paths", "games", "game_metadata", "play_stats", "emulator_status"]
        for table in expected_tables:
            assert table in tables

        # Check columns for 'games' table
        cursor.execute("PRAGMA table_info(games);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert "display_name" in columns
        assert "serial" in columns

        # Check columns for 'game_metadata' table
        cursor.execute("PRAGMA table_info(game_metadata);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert "cover_2d_path" in columns
        assert "cover_3d_path" in columns
        assert "is_favorite" in columns

        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [row[0] for row in cursor.fetchall()]
        expected_indexes = ["idx_games_platform", "idx_games_filepath", "idx_metadata_title"]
        for idx in expected_indexes:
            assert idx in indexes
