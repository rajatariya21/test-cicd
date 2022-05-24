clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.log' -delete

install-dev:
	pip3 install -r requirements-dev.txt
	pre-commit install

install:
	pip3 install -r requirements.txt

all: clean installs
