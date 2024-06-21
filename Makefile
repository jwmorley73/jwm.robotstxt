.PHONY: build install clean uninstall

venv=./.venv
python=$(venv)/bin/python
project=pyrobotstxt

default: uninstall clean install

build:
	$(python) -m build .

install:
	$(python) -m pip install .

clean:
	rm -rf ./build ./c-build ./dist

uninstall:
	$(python) -m pip uninstall -y $(project)

doc:
	cd ./docs && make html

test:
	$(python) -m pytest