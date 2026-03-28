"""Tests for promptlab store."""

from pathlib import Path

import pytest
from promptlab.prompt import Prompt
from promptlab.store import PromptStore


@pytest.fixture
def store(tmp_path: Path) -> PromptStore:
    s = PromptStore(tmp_path / ".prompts")
    s.init()
    return s


def test_store_init(store: PromptStore):
    assert store.root.exists()
    assert (store.root / "prompts.yaml").exists()


def test_store_save_and_load(store: PromptStore):
    p = Prompt(name="greeting", template="Hello {{name}}", variables={"name": str})
    version = store.save(p)
    assert version == 1

    loaded = store.load("greeting")
    assert loaded.name == "greeting"
    assert loaded.version == 1
    assert loaded.render(name="World") == "Hello World"


def test_store_auto_increment(store: PromptStore):
    p = Prompt(name="test", template="v1 content")
    assert store.save(p) == 1

    p.template = "v2 content"
    assert store.save(p) == 2

    p.template = "v3 content"
    assert store.save(p) == 3


def test_store_load_specific_version(store: PromptStore):
    p = Prompt(name="test", template="Version 1")
    store.save(p)
    p.template = "Version 2"
    store.save(p)

    v1 = store.load("test", version=1)
    v2 = store.load("test", version=2)
    assert v1.template == "Version 1"
    assert v2.template == "Version 2"


def test_store_list_prompts(store: PromptStore):
    store.save(Prompt(name="alpha", template="a"))
    store.save(Prompt(name="beta", template="b"))
    store.save(Prompt(name="beta", template="b2"))

    prompts = store.list_prompts()
    assert len(prompts) == 2
    beta = next(p for p in prompts if p["name"] == "beta")
    assert beta["latest_version"] == 2
    assert beta["version_count"] == 2


def test_store_history(store: PromptStore):
    p = Prompt(name="test", template="v1")
    store.save(p)
    p.template = "v2"
    store.save(p)

    hist = store.history("test")
    assert len(hist) == 2
    assert hist[0]["version"] == 1
    assert hist[1]["version"] == 2


def test_store_promote(store: PromptStore):
    p = Prompt(name="test", template="production ready")
    store.save(p)
    store.promote("test", version=1, env="production")

    loaded = store.load("test", env="production")
    assert loaded.version == 1


def test_store_not_found(store: PromptStore):
    with pytest.raises(FileNotFoundError):
        store.load("nonexistent")
