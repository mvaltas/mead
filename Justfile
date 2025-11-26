default: test

lint:
 uv run black . --check --diff --color

format:
 uv run black .

clean:
  rm -f dist/mead*.whl

test *params:
  uv run pytest -s {{params}}

build:
  uv build --wheel

version:
 uv run python -c 'import mead; print(mead.__version__);'

@run param:
 - uv run python {{param}}
