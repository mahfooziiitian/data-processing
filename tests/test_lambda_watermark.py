"""Tests for batch watermark persistence."""
from data_proc.lambda_arch import watermark


def test_read_watermark_missing_file_returns_zero(tmp_path):
    assert watermark.read_watermark(tmp_path / "missing.json") == 0


def test_write_then_read_watermark_roundtrips(tmp_path):
    watermark_path = tmp_path / "watermark.json"

    watermark.write_watermark(watermark_path, 7)

    assert watermark.read_watermark(watermark_path) == 7
