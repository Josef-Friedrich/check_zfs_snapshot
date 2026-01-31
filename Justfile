all: test format docs lint type_check

test:
	uv run --isolated --python=3.10 pytest
	uv run --isolated --python=3.11 pytest
	uv run --isolated --python=3.12 pytest
	uv run --isolated --python=3.13 pytest

test_quick:
	uv run --isolated --python=3.12 pytest

install: update

install_editable: install
	uv pip install --editable .

update:
	uv sync --upgrade

upgrade: update

build:
	uv build

publish:
	uv build
	uv publish

format:
	uv tool run ruff check --select I --fix .
	uv tool run ruff format

docs: docs_readme_patcher

docs_readme_patcher:
	uv tool run --isolated --with . readme-patcher

lint:
	uv tool run ruff check

type_check:
	uv run mypy check_zfs_snapshot.py tests
