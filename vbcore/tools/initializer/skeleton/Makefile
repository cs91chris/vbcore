PYVER=310
PACKAGE={skeleton}
LOG_LEVEL=DEBUG
REQ_PATH=requirements

export PIP_CONFIG_FILE=pip.conf
export VERSION="$(shell grep 'current_version' .bumpversion.cfg | sed 's/^[^=]*= *//')"


define bump_version
	bumpversion -n $(1) --verbose
	@( read -p "Are you sure?!? [Y/n]: " sure && case "$$sure" in [nN]) false;; *) true;; esac )
	bumpversion $(1) --verbose
endef

define copy_requirements
	cp ${REQ_PATH}/requirements-$(1).txt ${SERVICE_PATH}/$(2)/requirements.txt
endef

define req_compile
	pip-compile $(2) \
		--resolver=backtracking \
		--no-emit-trusted-host --no-emit-index-url --build-isolation \
		-o ${REQ_PATH}/$(1).txt ${REQ_PATH}/$(1).in
endef

define check_format
	$(shell ([ "${FMT_ONLY_CHECK}" = "true" ] && echo --check || echo ""))
endef


all: clean run-tox
lint: flake pylint mypy
security: safety liccheck bandit
radon: radon-cc radon-hal radon-mi radon-raw
cqa: radon-cc-report bandit-report radon bandit
format: autoflake black isort
dev: format lint security test


compile-deps:
	$(call req_compile,requirements-build)
	$(call req_compile,requirements)
	# extra requirements here
	$(call req_compile,requirements-test)
	$(call req_compile,requirements-dev)

upgrade-deps:
	$(call req_compile,requirements-build,--upgrade)
	$(call req_compile,requirements,--upgrade)
	# extra requirements here
	$(call req_compile,requirements-test,--upgrade)
	$(call req_compile,requirements-dev,--upgrade)

install-deps:
	pip install -r ${REQ_PATH}/requirements.txt
	pip install -r ${REQ_PATH}/requirements-test.txt
	pip install -r ${REQ_PATH}/requirements-dev.txt

clean-install-deps:
	pip install pip-tools
	pip-sync ${REQ_PATH}/requirements*.txt

clean:
	find . -name '*.pyc' -prune -exec rm -rf {} \;
	find . -name '__pycache__' -prune -exec rm -rf {} \;
	find . -name '.pytest_cache' -prune -exec rm -rf {} \;
	find ${PACKAGE} -name ".mypy_cache" -prune -exec rm -rf {} \;

autoflake:
	autoflake $(call check_format) \
		--recursive \
		--in-place \
		--remove-all-unused-imports \
		--ignore-init-module-imports \
		--remove-duplicate-keys \
		--remove-unused-variables \
		${PACKAGE} tests setup.py

black:
	black $(call check_format) \
		-t py${PYVER} --workers $(shell nproc) \
		${PACKAGE} sandbox tests setup.py

isort:
	isort $(call check_format) \
		--profile black -j $(shell nproc) --py ${PYVER} \
		--atomic \
		--overwrite-in-place \
		--combine-star \
		--combine-as \
		--dont-float-to-top \
		--honor-noqa \
		--force-alphabetical-sort-within-sections \
		--multi-line VERTICAL_HANGING_INDENT \
		${PACKAGE} tests setup.py

flake:
	flake8 \
		--config=.flake8 --statistics \
		${PACKAGE} tests setup.py

pylint:
	pylint \
		-j0 --rcfile=.pylintrc --reports=y \
		${PACKAGE} tests setup.py

mypy:
	mypy \
		--warn-unused-configs --no-strict-optional \
		${PACKAGE} tests

run-tox:
	tox \
		-vvv \
		--recreate \
		--exit-and-dump-after 180

test:
	PYTHONPATH=. pytest -v -rf --strict-markers \
		-p vbcore.tester.plugins.fixtures \
		-p vbcore.tester.plugins.startup \
		--cov=${PACKAGE} --cov-config .coveragerc \
		--cov-report=html \
		--cov-report=term-missing \
		tests

test-coverage:
	PYTHONPATH=. pytest -v -rf --strict-markers \
		-p vbcore.tester.plugins.fixtures \
		-p vbcore.tester.plugins.startup \
		--junitxml=junit-report.xml \
		--cov=${PACKAGE} --cov-config .coveragerc \
		--cov-report=xml \
		--cov-report=term-missing \
		tests

bandit:
	bandit -r ${PACKAGE}

bandit-report:
	bandit -f html \
		--ignore-nosec \
		--exit-zero \
		--silent \
		-r ${PACKAGE} > bandit-report.html

safety:
	safety check \
		-r ${REQ_PATH}/requirements.txt

liccheck:
	liccheck \
		--level PARANOID \
		-r ${REQ_PATH}/requirements.txt

radon-cc:
	# cyclomatic complexity
	radon cc \
		--total-average \
		--show-complexity \
		--min C \
		--order SCORE \
		${PACKAGE}

radon-cc-report:
	# cyclomatic complexity
	radon cc \
		--md \
		--total-average \
		--show-complexity \
		--min C \
		--order SCORE \
		${PACKAGE} > radon-cc-report.md

radon-mi:
	# maintainability index
	radon mi --min B --show ${PACKAGE}

radon-hal:
	# halstead metrics
	radon hal ${PACKAGE}

radon-raw:
	# raw metrics
	radon raw -s ${PACKAGE}

build-dist:
	python setup.py sdist bdist_wheel

build-cython:
	python setup.py bdist_wheel --cythonize

bump-build:
	$(call bump_version,build)

bump-release:
	$(call bump_version,release)

bump-major:
	$(call bump_version,major)

bump-minor:
	$(call bump_version,minor)

bump-patch:
	$(call bump_version,patch)
