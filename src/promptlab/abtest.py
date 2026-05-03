"""A/B testing for prompts — compare two versions on a dataset."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from promptlab.store import PromptStore


@dataclass
class ABResult:
    """Result of an A/B test."""

    prompt_name: str
    version_a: int
    version_b: int
    metric: str
    scores_a: list[float] = field(default_factory=list)
    scores_b: list[float] = field(default_factory=list)

    @property
    def avg_a(self) -> float:
        return sum(self.scores_a) / len(self.scores_a) if self.scores_a else 0.0

    @property
    def avg_b(self) -> float:
        return sum(self.scores_b) / len(self.scores_b) if self.scores_b else 0.0

    @property
    def winner(self) -> str:
        if not self.scores_a or not self.scores_b:
            return "inconclusive"
        if self.avg_a > self.avg_b:
            return f"v{self.version_a}"
        elif self.avg_b > self.avg_a:
            return f"v{self.version_b}"
        return "tie"

    @property
    def improvement_pct(self) -> float:
        """Percentage improvement of winner over loser."""
        if self.avg_a == 0 and self.avg_b == 0:
            return 0.0
        baseline = min(self.avg_a, self.avg_b)
        if baseline == 0:
            return 100.0
        return abs(self.avg_a - self.avg_b) / baseline * 100

    def summary(self) -> str:
        return (
            f"A/B Test: {self.prompt_name} (v{self.version_a} vs v{self.version_b})\n"
            f"  Metric: {self.metric}\n"
            f"  v{self.version_a}: avg={self.avg_a:.3f} ({len(self.scores_a)} samples)\n"
            f"  v{self.version_b}: avg={self.avg_b:.3f} ({len(self.scores_b)} samples)\n"
            f"  Winner: {self.winner} ({self.improvement_pct:.1f}% improvement)"
        )


# ─── Built-in metrics ──────────────────────────────────────────

def metric_length(rendered: str, _expected: str | None = None) -> float:
    """Metric: length of rendered prompt (lower = more concise)."""
    return float(len(rendered))


def metric_word_count(rendered: str, _expected: str | None = None) -> float:
    """Metric: word count of rendered prompt."""
    return float(len(rendered.split()))


def metric_exact_match(rendered: str, expected: str | None = None) -> float:
    """Metric: 1.0 if rendered matches expected, else 0.0."""
    if expected is None:
        return 0.0
    return 1.0 if rendered.strip() == expected.strip() else 0.0


BUILT_IN_METRICS: dict[str, Callable[..., float]] = {
    "length": metric_length,
    "word_count": metric_word_count,
    "exact_match": metric_exact_match,
}


class ABTest:
    """A/B test runner for comparing two prompt versions.

    Usage:
        test = ABTest(
            prompt_name="summarizer",
            version_a=3,
            version_b=4,
            dataset="eval/test.jsonl",
            metric="length",
        )
        results = test.run(store)
        print(results.summary())
    """

    def __init__(
        self,
        prompt_name: str,
        version_a: int,
        version_b: int,
        dataset: str | Path | list[dict[str, Any]] | None = None,
        metric: str | Callable[..., float] = "length",
    ) -> None:
        self.prompt_name = prompt_name
        self.version_a = version_a
        self.version_b = version_b
        self.dataset = dataset
        self.metric = metric

    def run(self, store: PromptStore | None = None, store_path: str = ".prompts") -> ABResult:
        """Run the A/B test."""
        if store is None:
            store = PromptStore(store_path)

        prompt_a = store.load(self.prompt_name, version=self.version_a)
        prompt_b = store.load(self.prompt_name, version=self.version_b)

        # Load dataset
        samples = self._load_dataset()

        # Get metric function
        metric_fn = self._get_metric()

        # Get metric name
        metric_name = self.metric if isinstance(self.metric, str) else self.metric.__name__

        result = ABResult(
            prompt_name=self.prompt_name,
            version_a=self.version_a,
            version_b=self.version_b,
            metric=metric_name,
        )

        for sample in samples:
            variables = sample.get("variables", sample)
            expected = sample.get("expected")

            try:
                rendered_a = prompt_a.render(**variables)
                score_a = metric_fn(rendered_a, expected)
                result.scores_a.append(score_a)
            except Exception:
                result.scores_a.append(0.0)

            try:
                rendered_b = prompt_b.render(**variables)
                score_b = metric_fn(rendered_b, expected)
                result.scores_b.append(score_b)
            except Exception:
                result.scores_b.append(0.0)

        return result

    def _load_dataset(self) -> list[dict[str, Any]]:
        """Load the test dataset."""
        if self.dataset is None:
            return [{}]  # Single empty sample (tests template itself)

        if isinstance(self.dataset, list):
            return self.dataset

        path = Path(self.dataset)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        if path.suffix == ".jsonl":
            return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        elif path.suffix == ".json":
            data = json.loads(path.read_text())
            return data if isinstance(data, list) else [data]
        else:
            raise ValueError(f"Unsupported dataset format: {path.suffix}")

    def _get_metric(self) -> Callable[..., float]:
        """Get the metric function."""
        if callable(self.metric):
            return self.metric

        if self.metric in BUILT_IN_METRICS:
            return BUILT_IN_METRICS[self.metric]

        raise ValueError(
            f"Unknown metric: '{self.metric}'. "
            f"Built-in: {list(BUILT_IN_METRICS.keys())}"
        )
