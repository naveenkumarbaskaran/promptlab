"""Tests for promptlab diff."""

from pathlib import Path

import pytest
from promptlab.prompt import Prompt
from promptlab.store import PromptStore
from promptlab.diff import diff_prompts, diff_summary


@pytest.fixture
def store(tmp_path: Path) -> PromptStore:
    s = PromptStore(tmp_path / ".prompts")
    s.init()
    return s


def test_diff_shows_changes(store: PromptStore):
    p = Prompt(name="test", template="Line one\nLine two\nLine three")
    store.save(p)
    p.template = "Line one\nLine TWO CHANGED\nLine three"
    store.save(p)

    result = diff_prompts(store, "test", v1=1, v2=2)
    assert "-Line two" in result
    assert "+Line TWO CHANGED" in result


def test_diff_no_changes(store: PromptStore):
    p = Prompt(name="test", template="Same content")
    store.save(p)
    store.save(Prompt(name="test", template="Same content"))

    result = diff_prompts(store, "test", v1=1, v2=2)
    assert result == ""


def test_diff_summary_counts(store: PromptStore):
    p = Prompt(name="test", template="A\nB\nC")
    store.save(p)
    p.template = "A\nX\nC\nD"
    store.save(p)

    summary = diff_summary(store, "test", v1=1, v2=2)
    assert summary["changed"] is True
    assert summary["added"] > 0 or summary["removed"] > 0
