# test_mock_sleep.py
import pytest
from unittest.mock import patch

from sleepy import sleep_add, sleep_multiply
# Patch time.sleep first to ensure it's replaced correctly
@patch("time.sleep", return_value=None)
def test_sleep_add(mock_sleep):
    result = sleep_add(2, 3)
    assert result == 5
    mock_sleep.assert_called_once_with(3)

@patch("time.sleep", return_value=None)  # Ensure this is correct order of patching
def test_sleep_multiply(mock_sleep):
    result = sleep_multiply(2, 3)
    assert result == 6
    mock_sleep.assert_called_once_with(5)

