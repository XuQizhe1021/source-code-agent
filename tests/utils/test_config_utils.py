import copy
import json

import app.utils.config as cfg


def _reset_runtime_config(monkeypatch, tmp_path):
    monkeypatch.setattr(cfg, "_config", None)
    monkeypatch.setattr(cfg, "CONFIG_PATH", str(tmp_path / "config.json"))


def test_load_config_uses_defaults_and_env(monkeypatch, tmp_path):
    _reset_runtime_config(monkeypatch, tmp_path)
    monkeypatch.setenv("NEO4J_URI", "bolt://127.0.0.1:7687")
    monkeypatch.setenv("OPENAI_API_KEY", "k-123")

    loaded = cfg.load_config()

    assert loaded["neo4j"]["uri"] == "bolt://127.0.0.1:7687"
    assert loaded["openai"]["api_key"] == "k-123"
    assert loaded["neo4j"]["database"] == "neo4j"


def test_load_config_merges_missing_keys_from_file(monkeypatch, tmp_path):
    _reset_runtime_config(monkeypatch, tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"neo4j": {"uri": "bolt://x"}}), encoding="utf-8")

    loaded = cfg.load_config()

    assert loaded["neo4j"]["uri"] == "bolt://x"
    assert loaded["neo4j"]["username"] == "neo4j"
    assert loaded["openai"]["model"] == "gpt-4"


def test_update_neo4j_config_persists_changes(monkeypatch, tmp_path):
    _reset_runtime_config(monkeypatch, tmp_path)
    ok = cfg.update_neo4j_config(uri="bolt://abc", username="u1", password="p1", database="d1")
    assert ok is True

    cfg._config = None
    reloaded = cfg.load_config()
    assert reloaded["neo4j"] == {
        "uri": "bolt://abc",
        "username": "u1",
        "password": "p1",
        "database": "d1",
    }


def test_update_openai_config_persists_changes(monkeypatch, tmp_path):
    _reset_runtime_config(monkeypatch, tmp_path)
    ok = cfg.update_openai_config(api_key="key-x", model="gpt-test")
    assert ok is True

    cfg._config = None
    reloaded = cfg.load_config()
    assert reloaded["openai"]["api_key"] == "key-x"
    assert reloaded["openai"]["model"] == "gpt-test"


def test_load_config_should_not_mutate_default_template(monkeypatch, tmp_path):
    original = copy.deepcopy(cfg.DEFAULT_CONFIG)
    _reset_runtime_config(monkeypatch, tmp_path)
    monkeypatch.setenv("NEO4J_URI", "bolt://changed-by-env")

    _ = cfg.load_config()

    assert cfg.DEFAULT_CONFIG == original
