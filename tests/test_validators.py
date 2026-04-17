from unittest.mock import patch
import pytest
import motoregis


def test_get_float_valid():
    with patch("builtins.input", return_value="14.5"):
        assert motoregis.get_float("test: ") == 14.5


def test_get_float_comma_separator():
    with patch("builtins.input", return_value="14,5"):
        assert motoregis.get_float("test: ") == 14.5


def test_get_float_negative_then_valid(capsys):
    with patch("builtins.input", side_effect=["-5", "10"]):
        result = motoregis.get_float("test: ")
    assert result == 10.0
    assert "0" in capsys.readouterr().out


def test_get_float_invalid_then_valid(capsys):
    with patch("builtins.input", side_effect=["abc", "3.5"]):
        result = motoregis.get_float("test: ")
    assert result == 3.5


def test_get_int_valid():
    with patch("builtins.input", return_value="100"):
        assert motoregis.get_int("test: ") == 100


def test_get_int_zero():
    with patch("builtins.input", return_value="0"):
        assert motoregis.get_int("test: ") == 0


def test_get_int_invalid_then_valid(capsys):
    with patch("builtins.input", side_effect=["abc", "42"]):
        result = motoregis.get_int("test: ")
    assert result == 42


def test_select_index_valid():
    with patch("builtins.input", return_value="2"):
        assert motoregis.select_index("test: ", 3) == 2


def test_select_index_zero():
    with patch("builtins.input", return_value="0"):
        assert motoregis.select_index("test: ", 3) == 0


def test_select_index_max():
    with patch("builtins.input", return_value="3"):
        assert motoregis.select_index("test: ", 3) == 3


def test_select_index_out_of_range_then_valid(capsys):
    with patch("builtins.input", side_effect=["5", "2"]):
        result = motoregis.select_index("test: ", 3)
    assert result == 2


def test_display_name_no_vehicle():
    assert motoregis.display_name("oil_change") == "Oil change"


def test_display_name_with_vehicle():
    vehicle = {"nomes_display": {"oil_change": "Oil & filter"}}
    assert motoregis.display_name("oil_change", vehicle) == "Oil & filter"


def test_display_name_fallback():
    vehicle = {"nomes_display": {}}
    assert motoregis.display_name("tire_pressure", vehicle) == "Tire pressure"
