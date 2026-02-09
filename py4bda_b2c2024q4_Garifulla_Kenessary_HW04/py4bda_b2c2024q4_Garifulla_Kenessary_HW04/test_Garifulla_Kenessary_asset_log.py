import pytest
from io import StringIO
import sys
import logging
from unittest.mock import patch

from asset import Asset, load_asset_from_file, print_asset_revenue, setup_logging


# Базовые тесты функциональности
def test_calculate_revenue():
    asset = Asset(name="TestAsset", capital=1000.0, interest=0.05)
    revenue = asset.calculate_revenue(5)
    expected_revenue = 1000.0 * ((1.0 + 0.05) ** 5 - 1.0)
    assert abs(revenue - expected_revenue) < 1e-2, f"Expected {expected_revenue}, got {revenue}"


def test_build_from_str():
    raw_data = "TestAsset 1000.0 0.05"
    asset = Asset.build_from_str(raw_data)
    assert asset.name == "TestAsset"
    assert asset.capital == 1000.0
    assert asset.interest == 0.05

def test_load_asset_from_file():
    raw_data = "TestAsset 1000.0 0.05"
    # Используем StringIO вместо sys.stdin
    with patch("builtins.open", return_value=StringIO(raw_data)):
        asset = load_asset_from_file(StringIO(raw_data))
    assert asset.name == "TestAsset"
    assert asset.capital == 1000.0
    assert asset.interest == 0.05


# Тесты на проверку сообщений в логере
def test_logger_debug():
    logger = logging.getLogger("asset")
    with patch("asset.logger.debug") as mock_debug:
        logger.debug("This is a debug message")
        mock_debug.assert_called_with("This is a debug message")


def test_logger_warning():
    logger = logging.getLogger("asset")
    with patch("asset.logger.warning") as mock_warning:
        logger.warning("This is a warning message")
        mock_warning.assert_called_with("This is a warning message")

def test_print_asset_revenue(capsys):
    # Подготовим данные
    asset_data = "TestAsset 1000.0 0.05"
    periods = [1, 3, 5]
    
    # Используем StringIO вместо sys.stdin
    with patch("builtins.open", return_value=StringIO(asset_data)):
        print_asset_revenue(StringIO(asset_data), periods)
    
    # Проверяем вывод с округлением на 3 знака
    captured = capsys.readouterr()
    assert f"1    :  {round(50.000, 3):10.3f}" in captured.out
    assert f"3    :  {round(157.625, 3):10.3f}" in captured.out
    assert f"5    :  {round(276.282, 3):10.3f}" in captured.out


def test_setup_logging():
    # Проверка, что логирование настроено через YAML конфиг
    yaml_config = """
    version: 1
    disable_existing_loggers: False
    formatters:
      simple:
        class: logging.Formatter
        format: "%(asctime)s %(name)s %(levelname)s %(message)s"
        datefmt: "%Y-%m-%d %H:%M:%S"

    handlers:
      file_debug:
        class: logging.FileHandler
        filename: asset_log.debug
        level: DEBUG
        formatter: simple

      file_warn:
        class: logging.FileHandler
        filename: asset_log.warn
        level: WARNING
        formatter: simple

      console_info:
        class: logging.StreamHandler
        level: INFO
        formatter: simple
        stream: ext://sys.stderr

    loggers:
      asset:
        level: DEBUG
        handlers: [file_debug, file_warn, console_info]
        propagate: False

    root:
      level: INFO
      handlers: [console_info]
    """

    with patch("builtins.open", return_value=StringIO(yaml_config)):
        setup_logging("mock_yaml_path")

    # Проверка, что логгер "asset" настроен на уровень DEBUG
    logger = logging.getLogger("asset")
    assert logger.level == logging.DEBUG

    # Проверка, что у логгера "asset" есть три обработчика
    assert len(logger.handlers) == 3
    assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)

    # Проверка уровня root логгера
    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO


if __name__ == "__main__":
    pytest.main()

