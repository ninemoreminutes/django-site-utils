PYTHON_MAJOR_MINOR := $(shell python -c "import sys; print('{0}{1}'.format(*sys.version_info))")
REQUIREMENTS_TXT = requirements$(PYTHON_MAJOR_MINOR).txt

.PHONY: core-requirements
core-requirements:
	pip install pip setuptools pip-tools

.PHONY: update-core-requirements
update-pip-requirements: core-requirements
	pip install -U pip setuptools pip-tools
	pip-compile -U requirements.in -o $(REQUIREMENTS_TXT)

.PHONY: requirements
requirements: core-requirements
	pip-sync $(REQUIREMENTS_TXT)

.PHONY: clean-pyc
clean-pyc:
	find . -iname "*.pyc" -delete
	find . -iname __pycache__ | xargs rm -rf

.PHONY: develop
develop: clean-pyc requirements
	python setup.py develop

.PHONY: check
check: develop
	python manage.py check

.PHONY: migrate
migrate: check
	python manage.py migrate --noinput --fake-initial

.PHONY: runserver
runserver: migrate
	python manage.py runserver

reports:
	mkdir -p $@

.PHONY: pycodestyle
pycodestyle: reports requirements
	set -o pipefail && $@ | tee reports/$@.report

.PHONY: flake8
flake8: reports requirements
	set -o pipefail && $@ | tee reports/$@.report

.PHONY: check8
check8: pycodestyle flake8

.PHONY: clean-coverage
clean-coverage:
	rm -f .coverage

.PHONY: test
test: clean-pyc requirements
	python setup.py test

.PHONY: clean-tox
clean-tox:
	rm -rf .tox

.PHONY: tox
tox: clean-pyc requirements
	tox

.PHONY: clean-all
clean-all: clean-pyc clean-coverage clean-tox
	rm -rf *.dist-info *.egg-info .eggs .cache build reports

.PHONY: bump-major
bump-major: requirements
	bump2version major

.PHONY: bump-minor
bump-minor: requirements
	bump2version minor

.PHONY: bump-patch
bump-patch: requirements
	bump2version patch

.PHONY: docs
docs: requirements
	python setup.py build_sphinx

.PHONY: dev-build
dev-build: requirements clean-pyc clean-coverage
	python setup.py dev_build

.PHONY: release-build
release-build: requirements clean-pyc clean-coverage
	python setup.py release_build

.PHONY: ship-it
ship-it: requirements clean-pyc clean-coverage
	python setup.py ship_it
