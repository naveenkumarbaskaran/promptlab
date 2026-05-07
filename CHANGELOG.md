# Changelog

## [2.0.0] - 2025-05-07

### Breaking Changes
- Development status upgraded to Production/Stable
- Added `jinja2` as a core dependency for advanced template rendering
- Bumped `pydantic` minimum to >=2.5

### Added
- Jinja2 template engine support for complex prompt templates
- `Typing :: Typed` classifier — fully typed package
- `prompt-management` keyword
- `mypy` in dev dependencies

### Improved
- Bumped `litellm` eval dep to >=1.40 for latest model support
- Bumped `ruff` to >=0.5, `pytest` to >=8.0
- Better variable validation with descriptive error messages
- Improved `Prompt.from_dict()` deserialization with `list` type support

### Fixed
- `PromptStore.save()` now handles concurrent writes safely
- `diff_prompts` correctly handles empty templates
- `ABTest` now validates sample sizes before running

---

## [1.0.0] - 2025-02-20

### Added
- Stable prompt versioning with file-based store
- A/B testing framework with statistical significance
- Environment-based prompt routing (dev/staging/prod)
- CLI: `promptlab init`, `promptlab save`, `promptlab diff`

### Improved
- YAML serialization with proper type preservation
- Prompt hash stability across Python versions

---

## [0.1.0] - 2025-01-05

### Added
- Initial release
- Core `Prompt` model with template rendering
- `PromptStore` file-based versioned storage
- `diff_prompts` for comparing versions
- `ABTest` for prompt evaluation
