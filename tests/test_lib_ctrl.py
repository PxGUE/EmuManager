import pytest
import logging
from unittest.mock import MagicMock, patch
from emumanager.controllers.lib_ctrl import LibraryController

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_scanner():
    return MagicMock()

@pytest.fixture
def lib_ctrl(mock_db, mock_scanner):
    return LibraryController(db=mock_db, scanner=mock_scanner)

def test_toggle_favorite_success(lib_ctrl, mock_db):
    # Setup
    game_id = 123
    is_favorite = True

    with patch("emumanager.controllers.lib_ctrl.EmuLog") as mock_log:
        # Execute
        lib_ctrl.toggle_favorite(game_id, is_favorite)

        # Verify database call
        mock_db.update_game_favorite.assert_called_once_with(game_id, is_favorite)

        # Verify logging
        mock_log.info.assert_called_once_with(f"Estado de favorito actualizado para {game_id}: {is_favorite}")

def test_toggle_favorite_failure(lib_ctrl, mock_db):
    # Setup
    game_id = 456
    is_favorite = False
    mock_db.update_game_favorite.side_effect = Exception("Database error")

    with patch("emumanager.controllers.lib_ctrl.EmuLog") as mock_log:
        # Execute
        lib_ctrl.toggle_favorite(game_id, is_favorite)

        # Verify database call was attempted
        mock_db.update_game_favorite.assert_called_once_with(game_id, is_favorite)

        # Verify error logging
        mock_log.error.assert_called_once_with(f"Error al actualizar favorito: Database error", exc_info=True)
