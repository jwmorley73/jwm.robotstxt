.PHONY: build install clean uninstall doc test lint

venv=./.venv
python=$(venv)/bin/python
project=jwm.robotstxt

default: uninstall clean install

build:
	$(python) -m build .

install:
	$(python) -m pip install .

clean:
	rm -rf ./build ./c-build ./dist ./lib ./wheelhouse || 0

uninstall:
	$(python) -m pip uninstall -y $(project)

doc:
	cd ./docs && make html

test:
	$(python) -m coverage run -m pytest ./tests

format: |
	$(python) -m isort --profile=black ./setup.py ./src ./tests
	$(python) -m black ./setup.py ./src ./tests
	find ./src -iname '*.cc' | xargs $(dir $(python))clang-format --style=Google -i