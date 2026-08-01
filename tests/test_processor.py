"""Basic tests for the processor module."""

from src.processor import transform


def test_transform_uppercases_input():
    assert transform("hello world") == "HELLO WORLD"


def test_transform_strips_trailing_newline():
    assert transform("hello\n") == "HELLO"


def test_transform_empty_string():
    assert transform("") == ""
