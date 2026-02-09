import os
import sys
import pytest
from task_Garifulla_Kenessary_bdt_web_spy import fetch_page, parse_page, main

# --- Unit test(s) (marked as slow) that do not require network access ---

@pytest.mark.slow
def test_parse_local_html(monkeypatch):
    """
    Use the local HTML dump (bdt_courses.html) to test that parse_page returns
    the expected email, F2F count (9) and online count (10).
    """
    local_file = "bdt_courses.html"
    assert os.path.exists(local_file), f"File {local_file} not found in working directory."
    with open(local_file, encoding="utf-8") as f:
        local_html = f.read()

    # Monkey-patch fetch_page so that any URL returns the local HTML
    monkeypatch.setattr("task_Ivanov_Ivan_bdt_web_spy.fetch_page", lambda url: local_html)

    html = fetch_page("http://dummyurl")
    email, f2f_count, online_count = parse_page(html)

    assert email == "study@bigdatateam.org", f"Expected email study@bigdatateam.org, got {email}"
    assert f2f_count == 9, f"Expected 9 F2F courses, got {f2f_count}"
    assert online_count == 10, f"Expected 10 online courses, got {online_count}"

@pytest.mark.slow
def test_cli_call_return_expected_summary(monkeypatch, capsys):
    """
    Simulate the CLI call (by setting sys.argv) and check that the output
    contains exactly 2 lines: one for F2F and one for online courses.
    """
    local_file = "bdt_courses.html"
    assert os.path.exists(local_file), f"File {local_file} not found in working directory."
    with open(local_file, encoding="utf-8") as f:
        local_html = f.read()

    monkeypatch.setattr("task_Ivanov_Ivan_bdt_web_spy.fetch_page", lambda url: local_html)
    test_args = ["task_Ivanov_Ivan_bdt_web_spy.py", "bigdatateam"]
    monkeypatch.setattr(sys, "argv", test_args)

    main()
    captured = capsys.readouterr().out.strip().splitlines()
    assert len(captured) == 2, f"stdout should contain exactly 2 lines, while you provided {len(captured)}"
    assert captured[0].startswith("F2F courses:"), "First line should start with 'F2F courses:'"
    assert captured[1].startswith("online courses:"), "Second line should start with 'online courses:'"

# --- Integration test(s) (marked as integration_test) that require network access ---

@pytest.mark.integration_test
def test_integration_live_vs_expected():
    """
    Download the live page from https://bigdatateam.org/ru/homework and compare the counts
    with those parsed from the expected HTML dump (bdt_courses_expected.html). If they differ,
    the assert error message must follow the given one‐line template.
    """
    expected_file = "bdt_courses_expected.html"
    assert os.path.exists(expected_file), f"File {expected_file} not found in working directory."
    with open(expected_file, encoding="utf-8") as f:
        expected_html = f.read()

    _, expected_f2f, expected_online = parse_page(expected_html)

    url = "https://bigdatateam.org/ru/homework"
    live_html = fetch_page(url)
    _, live_f2f, live_online = parse_page(live_html)

    msg = (f"expected F2F course count is {expected_f2f}, while you calculated {live_f2f}; "
           f"expected online course count is {expected_online}, while you calculated {live_online}")
    assert expected_f2f == live_f2f and expected_online == live_online, msg

@pytest.mark.integration_test
def test_integration_test_raise_expected_error():
    """
    Simulate a discrepancy in course counts and check that the raised assertion error message
    exactly follows the required template (one line, no line breaks).
    """
    expected_f2f = 10
    expected_online = 11
    live_f2f = 9
    live_online = 10
    error_msg = (f"expected F2F course count is {expected_f2f}, while you calculated {live_f2f}; "
                 f"expected online course count is {expected_online}, while you calculated {live_online}")
    with pytest.raises(AssertionError) as excinfo:
        assert expected_f2f == live_f2f and expected_online == live_online, error_msg
    assert str(excinfo.value) == error_msg

