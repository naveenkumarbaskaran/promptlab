"""Tests for promptlab A/B testing."""

from pathlib import Path

import pytest
from promptlab.prompt import Prompt
from promptlab.store import PromptStore
from promptlab.abtest import ABTest, metric_word_count, metric_exact_match


@pytest.fixture
def store(tmp_path: Path) -> PromptStore:
    s = PromptStore(tmp_path / ".prompts")
    s.init()
    p1 = Prompt(name="greet", template="Hello {{name}}", variables={"name": str})
    s.save(p1)
    p2 = Prompt(name="greet", template="Hi {{name}}! Welcome.", variables={"name": str})
    s.save(p2)
    return s


def test_abtest_length_metric(store: PromptStore):
    test = ABTest(
        prompt_name="greet",
        version_a=1,
        version_b=2,
        dataset=[{"variables": {"name": "Alice"}}],
        metric="length",
    )
    result = test.run(store)
    assert result.avg_a > 0
    assert result.avg_b > 0
    assert result.winner in ["v1", "v2"]


def test_abtest_custom_metric(store: PromptStore):
    def has_exclamation(rendered: str, _expected: str | None = None) -> float:
        return 1.0 if "!" in rendered else 0.0

    test = ABTest(
        prompt_name="greet",
        version_a=1,
        version_b=2,
        dataset=[{"variables": {"name": "Bob"}}],
        metric=has_exclamation,
    )
    result = test.run(store)
    assert result.avg_a == 0.0  # v1 has no !
    assert result.avg_b == 1.0  # v2 has !
    assert result.winner == "v2"


def test_abtest_summary(store: PromptStore):
    test = ABTest(
        prompt_name="greet",
        version_a=1,
        version_b=2,
        dataset=[{"variables": {"name": "Test"}}],
    )
    result = test.run(store)
    summary = result.summary()
    assert "greet" in summary
    assert "Winner" in summary


def test_abtest_jsonl_dataset(store: PromptStore, tmp_path: Path):
    dataset_path = tmp_path / "data.jsonl"
    dataset_path.write_text(
        '{"variables": {"name": "Alice"}}\n'
        '{"variables": {"name": "Bob"}}\n'
        '{"variables": {"name": "Charlie"}}\n'
    )

    test = ABTest(
        prompt_name="greet",
        version_a=1,
        version_b=2,
        dataset=str(dataset_path),
    )
    result = test.run(store)
    assert len(result.scores_a) == 3
    assert len(result.scores_b) == 3


def test_metric_exact_match():
    assert metric_exact_match("hello", "hello") == 1.0
    assert metric_exact_match("hello", "world") == 0.0
    assert metric_exact_match("hello", None) == 0.0


def test_metric_word_count():
    assert metric_word_count("one two three") == 3.0
