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

install: clean build
 pipx install --force dist/mead*.whl

@run param:
 - uv run python examples/{{param}}.py
