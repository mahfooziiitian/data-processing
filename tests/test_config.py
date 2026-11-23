"""Tests for resolving configured data paths."""
from pathlib import Path

from data_proc.config import _path_setting


def test_relative_override_resolves_against_data_home(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_PROC_HOME", str(tmp_path))
    monkeypatch.setenv("CUSTOMERS_CSV", "data/raw/customers.csv")

    assert _path_setting("CUSTOMERS_CSV", "unused") == tmp_path / "data/raw/customers.csv"


def test_absolute_override_ignores_data_home(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_PROC_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("CUSTOMERS_CSV", str(tmp_path / "elsewhere.csv"))

    assert _path_setting("CUSTOMERS_CSV", "unused") == Path(tmp_path / "elsewhere.csv")
