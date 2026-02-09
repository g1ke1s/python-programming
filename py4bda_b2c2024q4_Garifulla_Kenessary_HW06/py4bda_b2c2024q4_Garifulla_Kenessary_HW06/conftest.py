import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark a test as slow (unit test without network)")
    config.addinivalue_line("markers", "integration_test: mark a test as integration test (requires network)")

