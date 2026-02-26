import json

import pytest

import aslankigen.schema
from aslankigen.schema import generate, main


def test_generate_returns_valid_stable_json():
    """generate() returns valid JSON schema with a trailing newline, stable across calls."""
    result = generate()
    assert result.endswith("\n")
    parsed = json.loads(result)
    assert isinstance(parsed, dict)
    assert "properties" in parsed
    assert generate() == result


def test_main_writes_schema(tmp_path, monkeypatch):
    schema_file = tmp_path / "words.schema.json"
    monkeypatch.setattr(aslankigen.schema, "SCHEMA_FILE", schema_file)
    monkeypatch.setattr("sys.argv", ["schema"])

    main()

    assert schema_file.exists()
    assert isinstance(json.loads(schema_file.read_text()), dict)


def test_main_check_passes(tmp_path, monkeypatch):
    schema_file = tmp_path / "words.schema.json"
    schema_file.write_text(generate())
    monkeypatch.setattr(aslankigen.schema, "SCHEMA_FILE", schema_file)
    monkeypatch.setattr("sys.argv", ["schema", "--check"])

    main()


def test_main_check_fails_when_outdated(tmp_path, monkeypatch):
    schema_file = tmp_path / "words.schema.json"
    schema_file.write_text('{"stale": true}\n')
    monkeypatch.setattr(aslankigen.schema, "SCHEMA_FILE", schema_file)
    monkeypatch.setattr("sys.argv", ["schema", "--check"])

    with pytest.raises(SystemExit):
        main()


def test_main_check_fails_when_missing(tmp_path, monkeypatch):
    schema_file = tmp_path / "words.schema.json"
    monkeypatch.setattr(aslankigen.schema, "SCHEMA_FILE", schema_file)
    monkeypatch.setattr("sys.argv", ["schema", "--check"])

    with pytest.raises(SystemExit):
        main()
