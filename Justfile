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
  uv build

check: build
  uv run twine check dist/*

publish: build
  uv run twine upload dist/*

publish-test: build
  uv run twine upload --repository testpypi dist/*

version:
 uv run python -c 'import mead; print(mead.__version__);'

@run param:
 - uv run python {{param}}

alias ex := example

example name:
  uv run python ./examples/{{name}}.py

verify: (example "kaibab_plateau")

