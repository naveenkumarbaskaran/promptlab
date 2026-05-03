"""Prompt store — file-based versioned storage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from promptlab.prompt import Prompt


class PromptStore:
    """File-based prompt version store.

    Structure:
        .prompts/
        ├── my_prompt/
        │   ├── v1.yaml
        │   ├── v2.yaml
        │   └── metadata.yaml
        └── prompts.yaml  (registry)
    """

    def __init__(self, path: str | Path = ".prompts") -> None:
        self.root = Path(path)

    def init(self) -> None:
        """Initialize the prompt store directory."""
        self.root.mkdir(parents=True, exist_ok=True)
        registry = self.root / "prompts.yaml"
        if not registry.exists():
            registry.write_text(yaml.dump({"prompts": {}, "version": 1}))

    def save(self, prompt: Prompt) -> int:
        """Save a prompt, auto-incrementing the version. Returns new version."""
        prompt_dir = self.root / prompt.name
        prompt_dir.mkdir(parents=True, exist_ok=True)

        # Determine next version
        existing = self._get_versions(prompt.name)
        next_version = max(existing, default=0) + 1
        prompt.version = next_version

        # Write version file
        version_file = prompt_dir / f"v{next_version}.yaml"
        version_file.write_text(yaml.dump(prompt.to_dict(), default_flow_style=False))

        # Update metadata
        self._update_metadata(prompt)

        # Update registry
        self._update_registry(prompt.name, next_version)

        return next_version

    def load(self, name: str, version: int | None = None, env: str | None = None) -> Prompt:
        """Load a prompt by name and optional version or environment."""
        if env:
            version = self._get_env_version(name, env)

        if version is None:
            versions = self._get_versions(name)
            if not versions:
                raise FileNotFoundError(f"No versions found for prompt '{name}'")
            version = max(versions)

        version_file = self.root / name / f"v{version}.yaml"
        if not version_file.exists():
            raise FileNotFoundError(f"Version {version} not found for prompt '{name}'")

        data = yaml.safe_load(version_file.read_text())
        return Prompt.from_dict(data)

    def list_prompts(self) -> list[dict[str, Any]]:
        """List all prompts with their latest versions."""
        prompts = []
        if not self.root.exists():
            return prompts

        for child in sorted(self.root.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                versions = self._get_versions(child.name)
                if versions:
                    prompts.append({
                        "name": child.name,
                        "latest_version": max(versions),
                        "version_count": len(versions),
                    })
        return prompts

    def history(self, name: str) -> list[dict[str, Any]]:
        """Get version history for a prompt."""
        versions = self._get_versions(name)
        history = []
        for v in sorted(versions):
            try:
                prompt = self.load(name, version=v)
                history.append({
                    "version": v,
                    "hash": prompt.hash,
                    "created_at": prompt.created_at.isoformat() if prompt.created_at else "",
                    "metadata": prompt.metadata,
                })
            except Exception:
                history.append({"version": v, "error": "failed to load"})
        return history

    def promote(self, name: str, version: int, env: str) -> None:
        """Promote a specific version to an environment (e.g., 'production')."""
        metadata_file = self.root / name / "metadata.yaml"
        metadata: dict[str, Any] = {}
        if metadata_file.exists():
            metadata = yaml.safe_load(metadata_file.read_text()) or {}

        envs = metadata.get("environments", {})
        envs[env] = version
        metadata["environments"] = envs
        metadata_file.write_text(yaml.dump(metadata, default_flow_style=False))

    # ─── Private helpers ────────────────────────────────────────

    def _get_versions(self, name: str) -> list[int]:
        """Get all version numbers for a prompt."""
        prompt_dir = self.root / name
        if not prompt_dir.exists():
            return []
        versions = []
        for f in prompt_dir.glob("v*.yaml"):
            try:
                v = int(f.stem[1:])  # "v3" → 3
                versions.append(v)
            except ValueError:
                continue
        return sorted(versions)

    def _get_env_version(self, name: str, env: str) -> int:
        """Get the version promoted to a specific environment."""
        metadata_file = self.root / name / "metadata.yaml"
        if not metadata_file.exists():
            raise FileNotFoundError(f"No metadata for prompt '{name}'")
        metadata = yaml.safe_load(metadata_file.read_text()) or {}
        envs = metadata.get("environments", {})
        if env not in envs:
            raise KeyError(f"No version promoted to '{env}' for prompt '{name}'")
        return int(envs[env])

    def _update_metadata(self, prompt: Prompt) -> None:
        """Update prompt metadata file."""
        metadata_file = self.root / prompt.name / "metadata.yaml"
        metadata: dict[str, Any] = {}
        if metadata_file.exists():
            metadata = yaml.safe_load(metadata_file.read_text()) or {}
        metadata["name"] = prompt.name
        metadata["latest_version"] = prompt.version
        metadata["metadata"] = prompt.metadata
        metadata_file.write_text(yaml.dump(metadata, default_flow_style=False))

    def _update_registry(self, name: str, version: int) -> None:
        """Update the global registry."""
        registry_file = self.root / "prompts.yaml"
        registry: dict[str, Any] = {"prompts": {}, "version": 1}
        if registry_file.exists():
            registry = yaml.safe_load(registry_file.read_text()) or registry
        registry["prompts"][name] = {"latest_version": version}
        registry_file.write_text(yaml.dump(registry, default_flow_style=False))
