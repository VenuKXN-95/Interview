"""
Unit tests for LLM response parser.
"""
import pytest
from app.llm.response_parser import extract_json


class TestExtractJson:
    def test_direct_json(self):
        raw = '{"name": "John", "score": 7}'
        result = extract_json(raw)
        assert result == {"name": "John", "score": 7}

    def test_json_in_markdown_fence(self):
        raw = '```json\n{"name": "John", "score": 8}\n```'
        result = extract_json(raw)
        assert result["name"] == "John"
        assert result["score"] == 8

    def test_json_with_prose_before(self):
        raw = 'Here is the result:\n{"name": "Jane", "age": 30}'
        result = extract_json(raw)
        assert result["name"] == "Jane"

    def test_json_array(self):
        raw = '[{"q": "Tell me about yourself"}, {"q": "What is DI?"}]'
        result = extract_json(raw)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_trailing_comma_cleaned(self):
        raw = '{"name": "John", "skills": ["Python", "Go",]}'
        result = extract_json(raw)
        assert result is not None
        assert "Python" in result["skills"]

    def test_empty_string_returns_none(self):
        assert extract_json("") is None

    def test_invalid_returns_none(self):
        assert extract_json("This is not JSON at all!") is None
