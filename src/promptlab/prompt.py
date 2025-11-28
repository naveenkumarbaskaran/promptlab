"""Core Prompt model — typed template with variable validation."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any


# Template variable pattern: {{variable_name}}
_VAR_PATTERN = re.compile(r"\{\{(\w+)\}\}")


class Prompt:
    """A versioned, typed prompt template.

    Usage:
        prompt = Prompt(
            name="greeting",
            template="Hello {{name}}, you are a {{role}}.",
            variables={"name": str, "role": str},
        )
        rendered = prompt.render(name="Alice", role="developer")
        # "Hello Alice, you are a developer."
    """

    def __init__(
        self,
        name: str,
        template: str,
        variables: dict[str, type] | None = None,
        defaults: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        version: int = 0,
    ) -> None:
        self.name = name
        self.template = template
        self.variables = variables or {}
        self.defaults = defaults or {}
        self.metadata = metadata or {}
        self.version = version
        self.created_at = datetime.now(timezone.utc)

        # Auto-discover variables from template if not explicitly provided
        if not self.variables:
            discovered = _VAR_PATTERN.findall(template)
            self.variables = {v: str for v in discovered}

    @property
    def hash(self) -> str:
        """Stable hash of the template content."""
        return hashlib.sha256(self.template.encode()).hexdigest()[:16]

    @property
    def variable_names(self) -> list[str]:
        """Names of all variables in the template."""
        return sorted(self.variables.keys())

    @property
    def template_variables(self) -> list[str]:
        """Variables actually referenced in the template text."""
        return _VAR_PATTERN.findall(self.template)

    def render(self, **kwargs: Any) -> str:
        """Render the template with validated variables.

        Raises:
            TypeError: If a variable has the wrong type or is missing.
        """
        # Apply defaults
        for var, default in self.defaults.items():
            if var not in kwargs:
                kwargs[var] = default

        # Check required variables
        for var_name, var_type in self.variables.items():
            if var_name not in kwargs:
                raise TypeError(
                    f"Missing required variable '{var_name}' for prompt '{self.name}'. "
                    f"Required: {self.variable_names}"
                )

            value = kwargs[var_name]
            if not isinstance(value, var_type):
                raise TypeError(
                    f"Variable '{var_name}' must be {var_type.__name__}, "
                    f"got {type(value).__name__}"
                )

        # Render
        result = self.template
        for var_name, value in kwargs.items():
            result = result.replace(f"{{{{{var_name}}}}}", str(value))

        return result

    def validate(self) -> list[str]:
        """Validate the prompt template. Returns list of issues."""
        issues: list[str] = []

        # Check for undefined variables in template
        template_vars = set(self.template_variables)
        defined_vars = set(self.variables.keys())

        undefined = template_vars - defined_vars
        if undefined:
            issues.append(f"Variables in template but not defined: {undefined}")

        unused = defined_vars - template_vars
        if unused:
            issues.append(f"Variables defined but not in template: {unused}")

        # Check for empty template
        if not self.template.strip():
            issues.append("Template is empty")

        return issues

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict (for YAML storage)."""
        return {
            "name": self.name,
            "version": self.version,
            "template": self.template,
            "variables": {k: v.__name__ for k, v in self.variables.items()},
            "defaults": self.defaults,
            "metadata": self.metadata,
            "hash": self.hash,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Prompt:
        """Deserialize from dict."""
        type_map = {"str": str, "int": int, "float": float, "bool": bool}
        variables = {
            k: type_map.get(v, str)
            for k, v in data.get("variables", {}).items()
        }
        return cls(
            name=data["name"],
            template=data["template"],
            variables=variables,
            defaults=data.get("defaults", {}),
            metadata=data.get("metadata", {}),
            version=data.get("version", 0),
        )

    def __repr__(self) -> str:
        return f"Prompt(name='{self.name}', version={self.version}, vars={self.variable_names})"
