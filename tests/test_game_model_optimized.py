import unittest.mock as mock
import pytest
# dependencies are now handled by conftest.py or mocker
from emumanager.controllers.game_model import GameListModel

@pytest.fixture
def model():
    m = GameListModel()
    # Simulate some games
    games = [
        {"id": 1, "title": "Mario", "is_favorite": 0, "file_hash": "h1", "file_path": "p1", "platform": "nes"},
        {"id": 2, "title": "Zelda", "is_favorite": 1, "file_hash": "h2", "file_path": "p2", "platform": "nes"},
        {"id": 3, "title": "Metroid", "is_favorite": 0, "file_hash": "h3", "file_path": "p3", "platform": "nes"}
    ]
    m._all_results = games
    m._id_to_game = {int(g.get("id", -1)): g for g in games}
    m._apply_filter()
    return m

def test_favorite_toggle_updates_memory(model):
    # Toggle Mario to favorite
    model.set_favorite_locally(1, True)
    assert model._id_to_game[1]["is_favorite"] == 1

    # Toggle Zelda to not favorite
    model.set_favorite_locally(2, False)
    assert model._id_to_game[2]["is_favorite"] == 0

def test_favorite_toggle_emits_data_changed(model):
    # We don't patch, we trust the conftest mock
    model.set_favorite_locally(3, True)
    # Metroid is at index 2
    model.dataChanged.emit.assert_called()
    args, _ = model.dataChanged.emit.call_args
    assert args[0].row() == 2
    assert args[1].row() == 2
    assert GameListModel.IsFavoriteRole in args[2]

def test_favorites_only_filter(model):
    model.showFavoritesOnly = True
    # Initially only Zelda (ID 2) is favorite
    assert model.rowCount() == 1
    assert model._games[0]["id"] == 2

    # Toggle Mario (ID 1) to favorite
    model.set_favorite_locally(1, True)
    # Since showFavoritesOnly is True, set_favorite_locally calls beginResetModel/endResetModel
    assert model.rowCount() == 2
    assert any(g["id"] == 1 for g in model._games)

    # Toggle Zelda to not favorite
    model.set_favorite_locally(2, False)
    assert model.rowCount() == 1
    assert model._games[0]["id"] == 1

def test_lookup_missing_game(model):
    # Should not crash
    model.set_favorite_locally(999, True)
