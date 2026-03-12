"""Tests for promptlab Prompt model."""

import pytest
from promptlab.prompt import Prompt


def test_prompt_render():
    p = Prompt(
        name="greeting",
        template="Hello {{name}}, you are a {{role}}.",
        variables={"name": str, "role": str},
    )
    result = p.render(name="Alice", role="developer")
    assert result == "Hello Alice, you are a developer."


def test_prompt_auto_discover_variables():
    p = Prompt(name="test", template="Hi {{name}} from {{city}}")
    assert sorted(p.variable_names) == ["city", "name"]


def test_prompt_missing_variable():
    p = Prompt(name="test", template="Hello {{name}}", variables={"name": str})
    with pytest.raises(TypeError, match="Missing required variable"):
        p.render()


def test_prompt_wrong_type():
    p = Prompt(name="test", template="Order {{order_id}}", variables={"order_id": str})
    with pytest.raises(TypeError, match="must be str"):
        p.render(order_id=123)


def test_prompt_defaults():
    p = Prompt(
        name="test",
        template="Priority: {{priority}}",
        variables={"priority": str},
        defaults={"priority": "Medium"},
    )
    assert p.render() == "Priority: Medium"
    assert p.render(priority="High") == "Priority: High"


def test_prompt_hash_stable():
    p1 = Prompt(name="a", template="Hello world")
    p2 = Prompt(name="b", template="Hello world")
    assert p1.hash == p2.hash


def test_prompt_hash_changes():
    p1 = Prompt(name="a", template="Hello world")
    p2 = Prompt(name="a", template="Hello world!")
    assert p1.hash != p2.hash


def test_prompt_validate_ok():
    p = Prompt(name="test", template="Hi {{name}}", variables={"name": str})
    assert p.validate() == []


def test_prompt_validate_undefined():
    p = Prompt(name="test", template="Hi {{name}} from {{city}}", variables={"name": str})
    issues = p.validate()
    assert any("not defined" in i for i in issues)


def test_prompt_validate_unused():
    p = Prompt(
        name="test",
        template="Hello {{name}}",
        variables={"name": str, "unused_var": str},
    )
    issues = p.validate()
    assert any("not in template" in i for i in issues)


def test_prompt_validate_empty():
    p = Prompt(name="test", template="  ", variables={})
    issues = p.validate()
    assert any("empty" in i.lower() for i in issues)


def test_prompt_serialization():
    p = Prompt(
        name="test",
        template="Hello {{name}}",
        variables={"name": str},
        metadata={"author": "test"},
        version=3,
    )
    data = p.to_dict()
    p2 = Prompt.from_dict(data)
    assert p2.name == "test"
    assert p2.version == 3
    assert p2.render(name="World") == "Hello World"


def test_prompt_repr():
    p = Prompt(name="test", template="Hi {{x}}", version=2)
    assert "test" in repr(p)
    assert "2" in repr(p)
