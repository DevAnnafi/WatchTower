import pytest

from watchtower.parser import extract_text


def test_extract_removes_scripts():
    assert extract_text("<h1>Hello</h1><script>bad()</script>") == "Hello"

def test_selector():
    assert extract_text("<p>A</p><p class='x'>B</p>", ".x") == "B"

def test_missing_selector():
    with pytest.raises(ValueError): extract_text("<p>A</p>", ".missing")
