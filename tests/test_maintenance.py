import json
import pytest
import motoregis


def _write_csv(path, rows):
    path.write_text("\n".join(",".join(str(c) for c in row) for row in rows) + "\n")


def _write_vehicle(path, maintenance: dict):
    vehicle = {
        "veiculo": "Test Vehicle",
        "nomes_display": {"oil_change": "Oil & filter", "tire_pressure": "Tire pressure"},
        "manutencoes": maintenance,
    }
    path.write_text(json.dumps(vehicle))


def test_check_maintenance_km_alert(tmp_path, monkeypatch, capsys):
    csv_file = tmp_path / "vehicle.csv"
    json_file = tmp_path / "vehicle.json"
    _write_csv(csv_file, [
        ["date", "odometer", "category", "cost", "liters", "details"],
        ["2026-01-01", "10000", "1", "85.00", "14.00", "gasoline"],
    ])
    _write_vehicle(json_file, {"por_quilometragem": {"oil_change": 500}, "por_tempo_meses": {}, "por_tempo_dias": {}})
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))

    motoregis.check_maintenance("vehicle.csv", "vehicle.json", 10600, "2026-01-20")

    out = capsys.readouterr().out
    assert "Oil & filter" in out
    assert "600 km ago" in out


def test_check_maintenance_no_alert(tmp_path, monkeypatch, capsys):
    csv_file = tmp_path / "vehicle.csv"
    json_file = tmp_path / "vehicle.json"
    _write_csv(csv_file, [
        ["date", "odometer", "category", "cost", "liters", "details"],
        ["2026-01-01", "10000", "1", "85.00", "14.00", "gasoline"],
    ])
    _write_vehicle(json_file, {"por_quilometragem": {"oil_change": 5000}, "por_tempo_meses": {}, "por_tempo_dias": {}})
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))

    motoregis.check_maintenance("vehicle.csv", "vehicle.json", 10200, "2026-01-10")

    out = capsys.readouterr().out
    assert "Pending maintenance" not in out


def test_check_maintenance_months_alert(tmp_path, monkeypatch, capsys):
    csv_file = tmp_path / "vehicle.csv"
    json_file = tmp_path / "vehicle.json"
    _write_csv(csv_file, [
        ["date", "odometer", "category", "cost", "liters", "details"],
        ["2025-01-01", "10000", "1", "85.00", "14.00", "gasoline"],
    ])
    _write_vehicle(json_file, {"por_quilometragem": {}, "por_tempo_meses": {"oil_change": 6}, "por_tempo_dias": {}})
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))

    motoregis.check_maintenance("vehicle.csv", "vehicle.json", 10200, "2026-01-01")

    out = capsys.readouterr().out
    assert "Oil & filter" in out
    assert "months ago" in out


def test_check_maintenance_days_alert(tmp_path, monkeypatch, capsys):
    csv_file = tmp_path / "vehicle.csv"
    json_file = tmp_path / "vehicle.json"
    _write_csv(csv_file, [
        ["date", "odometer", "category", "cost", "liters", "details"],
        ["2026-01-01", "10000", "1", "85.00", "14.00", "gasoline"],
    ])
    _write_vehicle(json_file, {"por_quilometragem": {}, "por_tempo_meses": {}, "por_tempo_dias": {"tire_pressure": 15}})
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))

    motoregis.check_maintenance("vehicle.csv", "vehicle.json", 10200, "2026-01-20")

    out = capsys.readouterr().out
    assert "Tire pressure" in out
    assert "days ago" in out


def test_check_maintenance_resets_after_service(tmp_path, monkeypatch, capsys):
    csv_file = tmp_path / "vehicle.csv"
    json_file = tmp_path / "vehicle.json"
    _write_csv(csv_file, [
        ["date", "odometer", "category", "cost", "liters", "details"],
        ["2026-01-01", "10000", "1", "85.00", "14.00", "gasoline"],
        ["2026-01-10", "10600", "2", "50.00", "0.00", "oil_change"],
    ])
    _write_vehicle(json_file, {"por_quilometragem": {"oil_change": 500}, "por_tempo_meses": {}, "por_tempo_dias": {}})
    monkeypatch.setattr(motoregis, "DATA_DIR", str(tmp_path))

    motoregis.check_maintenance("vehicle.csv", "vehicle.json", 10700, "2026-01-20")

    out = capsys.readouterr().out
    assert "Oil & filter" not in out
