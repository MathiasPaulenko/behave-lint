# Release Checklist

Pre-release checklist for `behave-lint` releases.

## Pre-release

- [ ] All tests pass: `uv run pytest -m "not performance and not slow"`
- [ ] Lint clean: `uv run ruff check src/ tests/`
- [ ] Type check clean: `uv run mypy src/`
- [ ] Docs build clean: `uv run mkdocs build --strict`
- [ ] Version bumped in `pyproject.toml`, `src/behave_lint/version.py`,
      `src/behave_lint/__init__.py`
- [ ] `CHANGELOG.md` updated with release date and entries
- [ ] `README.md` is up to date
- [ ] All example projects in `examples/` are runnable
- [ ] Performance benchmarks pass: `uv run pytest -m performance -v`

## Release candidate (for minor/major releases)

- [ ] Create `release/v<x.y.z>` branch from `main`
- [ ] Tag `v<x.y.z>-rc1` and push
- [ ] Verify release workflow dry-run passes
- [ ] Test RC install: `pip install behave-lint==<x.y.z>rc1`
- [ ] Test in a real project
- [ ] If issues found, fix on release branch and tag `rc2`

## Final release

- [ ] Tag `v<x.y.z>` on release branch (or `main` for patches)
- [ ] Push tag: `git push origin v<x.y.z>`
- [ ] Release workflow triggers automatically
- [ ] Verify package appears on [PyPI](https://pypi.org/project/behave-lint/)
- [ ] Verify GitHub Release is created with auto-generated notes
- [ ] Verify docs site is updated (GitHub Pages deploy)
- [ ] Announce release (GitHub Release, social media, Behave community)

## Post-release

- [ ] Merge release branch back to `main` (if applicable)
- [ ] Update `CHANGELOG.md` `[Unreleased]` section
- [ ] Close milestone in GitHub
- [ ] Update project board
