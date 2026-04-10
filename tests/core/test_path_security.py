import pytest
from pathlib import Path
from emumanager.core.security import PathSecurity

def test_safe_join_basic(tmp_path):
    base = tmp_path / "base"
    base.mkdir()

    result = PathSecurity.safe_join(base, "subdir", "file.txt")
    assert result == (base / "subdir" / "file.txt").resolve()

def test_safe_join_traversal_parent(tmp_path):
    base = tmp_path / "base"
    base.mkdir()

    # Intento de subir un nivel
    result = PathSecurity.safe_join(base, "..", "other.txt")
    assert result is None

def test_safe_join_traversal_complex(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    (tmp_path / "secret").mkdir()

    result = PathSecurity.safe_join(base, "../secret/file.txt")
    assert result is None

def test_safe_join_absolute_path_simulation(tmp_path):
    base = tmp_path / "base"
    base.mkdir()

    # En muchos sistemas, joinpath con algo que empieza con / lo toma como absoluto
    # Pero nuestro safe_join hace lstrip('/')
    result = PathSecurity.safe_join(base, "/etc/passwd")
    # Debería ser base / etc / passwd
    assert result == (base / "etc" / "passwd").resolve()

def test_sanitize_id():
    assert PathSecurity.sanitize_id("valid_id") == "valid_id"
    assert PathSecurity.sanitize_id("../invalid/id") == "invalidid"
    assert PathSecurity.sanitize_id("id\\with\\backslashes") == "idwithbackslashes"
    assert PathSecurity.sanitize_id("id/with/slashes") == "idwithslashes"
