"""Prompt diffing — compare two versions side by side."""

from __future__ import annotations

import difflib

from promptlab.store import PromptStore


def diff_prompts(
    store: PromptStore,
    name: str,
    v1: int,
    v2: int,
    context_lines: int = 3,
) -> str:
    """Generate a unified diff between two prompt versions.

    Args:
        store: The prompt store
        name: Prompt name
        v1: First version number
        v2: Second version number
        context_lines: Number of context lines in diff

    Returns:
        Unified diff string
    """
    prompt_v1 = store.load(name, version=v1)
    prompt_v2 = store.load(name, version=v2)

    lines_v1 = prompt_v1.template.splitlines(keepends=True)
    lines_v2 = prompt_v2.template.splitlines(keepends=True)

    diff = difflib.unified_diff(
        lines_v1,
        lines_v2,
        fromfile=f"{name}/v{v1}",
        tofile=f"{name}/v{v2}",
        n=context_lines,
    )

    return "".join(diff)


def diff_summary(store: PromptStore, name: str, v1: int, v2: int) -> dict[str, int]:
    """Get a summary of changes between two versions.

    Returns:
        Dict with 'added', 'removed', 'changed' line counts.
    """
    prompt_v1 = store.load(name, version=v1)
    prompt_v2 = store.load(name, version=v2)

    lines_v1 = prompt_v1.template.splitlines()
    lines_v2 = prompt_v2.template.splitlines()

    matcher = difflib.SequenceMatcher(None, lines_v1, lines_v2)

    added = 0
    removed = 0
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "insert":
            added += j2 - j1
        elif op == "delete":
            removed += i2 - i1
        elif op == "replace":
            added += j2 - j1
            removed += i2 - i1

    return {
        "added": added,
        "removed": removed,
        "total_lines_v1": len(lines_v1),
        "total_lines_v2": len(lines_v2),
        "hash_v1": prompt_v1.hash,
        "hash_v2": prompt_v2.hash,
        "changed": prompt_v1.hash != prompt_v2.hash,
    }
