import json
import pytest
import motoregis


def test_load_json_valid(tmp_path, monkeypatch):
    config = {"key": "value", "number": 42}
    p = tmp_path / "test.json"
    p.write_text(json.dumps(config))
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))
    assert motoregis.load_json("test.json") == config


def test_load_json_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))
    assert motoregis.load_json("nonexistent.json") is None


def test_load_json_invalid_json(tmp_path, monkeypatch):
    p = tmp_path / "bad.json"
    p.write_text("{not valid json}")
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))
    assert motoregis.load_json("bad.json") is None


def test_read_csv_valid(tmp_path, monkeypatch):
    p = tmp_path / "data.csv"
    p.write_text("date,odometer,category,cost,liters,details\n2026-01-01,10000,1,85.50,14.5,gasoline\n")
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))
    rows = motoregis.read_csv("data.csv")
    assert rows[0] == ["date", "odometer", "category", "cost", "liters", "details"]
    assert rows[1] == ["2026-01-01", "10000", "1", "85.50", "14.5", "gasoline"]


def test_read_csv_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))
    assert motoregis.read_csv("nonexistent.csv") == []


def test_append_and_read_record(tmp_path, monkeypatch):
    p = tmp_path / "data.csv"
    p.write_text("date,odometer,category,cost,liters,details\n")
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))
    motoregis.append_record("data.csv", ["2026-01-01", 10000, 1, "85.50", "14.50", "gasoline"])
    rows = motoregis.read_csv("data.csv")
    assert len(rows) == 2
    assert rows[1] == ["2026-01-01", "10000", "1", "85.50", "14.50", "gasoline"]


def test_get_last_odometer_empty(tmp_path, monkeypatch):
    p = tmp_path / "data.csv"
    p.write_text("date,odometer,category,cost,liters,details\n")
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))
    assert motoregis.get_last_odometer("data.csv") == 0


def test_get_last_odometer_with_records(tmp_path, monkeypatch):
    p = tmp_path / "data.csv"
    p.write_text(
        "date,odometer,category,cost,liters,details\n"
        "2026-01-01,10000,1,85.50,14.50,gasoline\n"
        "2026-01-15,10500,1,90.00,15.00,gasoline\n"
    )
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))
    assert motoregis.get_last_odometer("data.csv") == 10500


def test_get_last_fuel_record(tmp_path, monkeypatch):
    p = tmp_path / "data.csv"
    p.write_text(
        "date,odometer,category,cost,liters,details\n"
        "2026-01-01,10000,1,85.50,14.50,gasoline\n"
        "2026-01-10,10200,2,50.00,0.00,oil_change\n"
        "2026-01-15,10500,1,90.00,15.00,gasoline\n"
    )
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))
    odo, liters = motoregis.get_last_fuel_record("data.csv")
    assert odo == 10500
    assert liters == 15.0


def test_get_last_fuel_record_none(tmp_path, monkeypatch):
    p = tmp_path / "data.csv"
    p.write_text("date,odometer,category,cost,liters,details\n")
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))
    odo, liters = motoregis.get_last_fuel_record("data.csv")
    assert odo is None
    assert liters is None
