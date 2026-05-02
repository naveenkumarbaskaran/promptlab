# Contributing to promptlab

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/naveenkumarbaskaran/promptlab.git
cd promptlab
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Style

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
ruff check .
ruff format .
```

## Making Changes

1. Fork the repo and create a feature branch from `main`
2. Make your changes with clear, descriptive commits
3. Add or update tests for any new functionality
4. Ensure all tests pass and linting is clean
5. Open a pull request against `main`

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add Jinja2 template support`
- `fix: handle empty prompt body in store`
- `test: add A/B test with async metrics`
- `docs: add deployment workflow example`

## Adding New Features

- **New variable types** → extend `VariableType` enum and validation in `prompt.py`
- **New storage backends** → subclass the store interface in `store.py`
- **New diff formats** → add formatter in `diff.py`
- **New built-in metrics** → add to `BUILT_IN_METRICS` in `abtest.py`
- **New CLI commands** → add subparser in `cli.py`

## Prompt Store Format

Prompts are stored as YAML files in `.prompts/`:

```
.prompts/
  my-prompt/
    v1.yaml
    v2.yaml
    meta.yaml    # tracks latest version, environments
```

When modifying store internals, ensure backward compatibility with existing `.prompts/` directories.

## Reporting Issues

- Use GitHub Issues with a clear title and reproduction steps
- Include your Python version and promptlab version
- For A/B test issues, include the metric function and dataset format

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
