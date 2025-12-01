default: test



lint:
 uv run black . --check --diff --color

format:
 uv run black .

install:
  uv sync --all-extras

clean:
  rm -f dist/mead*.whl
  rm -f dist/mead*.tar.gz

test *params:
  uv run pytest -s {{params}}

build:
  uv build

check: build
  uv run twine check dist/*

publish: build
  uv run twine upload dist/*

publish-test: clean build test
  uv run twine upload --repository testpypi dist/*

version:
 uv run python -c 'import mead; print(mead.__version__);'

@run param:
 - uv run python {{param}}

alias ex := example

example name:
  uv run python ./examples/{{name}}.py

verify: (example "kaibab_plateau")

