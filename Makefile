PACKAGE=vbcore
PYVER=39
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
		--no-emit-trusted-host --no-emit-index-url --build-isolation \
		-o ${REQ_PATH}/$(1).txt ${REQ_PATH}/$(1).in
endef

define check_format
	$(shell ([ "${FMT_ONLY_CHECK}" = "true" ] && echo --check || echo ""))
endef


all: clean run-tox
lint: flake pylint mypy
security: safety liccheck
format: autoflake black isort
dev: format lint test-coverage


compile-deps:
	$(call req_compile,requirements)
	$(call req_compile,requirements-build)
	$(call req_compile,requirements-db)
	$(call req_compile,requirements-http)
	$(call req_compile,requirements-crypto)
	$(call req_compile,requirements-net)
	$(call req_compile,requirements-test)
	$(call req_compile,requirements-dev)

upgrade-deps:
	$(call req_compile,requirements,--upgrade)
	$(call req_compile,requirements-build,--upgrade)
	$(call req_compile,requirements-db,--upgrade)
	$(call req_compile,requirements-http,--upgrade)
	$(call req_compile,requirements-crypto,--upgrade)
	$(call req_compile,requirements-net,--upgrade)
	$(call req_compile,requirements-test,--upgrade)
	$(call req_compile,requirements-dev,--upgrade)

install-deps:
	pip install \
		-r ${REQ_PATH}/requirements.txt \
		-r ${REQ_PATH}/requirements-db.txt \
		-r ${REQ_PATH}/requirements-http.txt \
		-r ${REQ_PATH}/requirements-crypto.txt \
		-r ${REQ_PATH}/requirements-net.txt \
		-r ${REQ_PATH}/requirements-test.txt \
		-r ${REQ_PATH}/requirements-dev.txt

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
		--recursive --in-place \
		--remove-all-unused-imports --ignore-init-module-imports \
		--remove-duplicate-keys --remove-unused-variables \
		vbcore tests setup.py
black:
	black $(call check_format) \
		-t py${PYVER} --workers $(shell nproc) \
		${PACKAGE} sandbox tests setup.py

isort:
	isort $(call check_format) \
		--profile black -j $(shell nproc) --py ${PYVER} \
		--atomic --overwrite-in-place \
		--combine-star --combine-as --dont-float-to-top --honor-noqa \
		--force-alphabetical-sort-within-sections --multi-line VERTICAL_HANGING_INDENT \
		vbcore tests setup.py

flake:
	flake8 --config=.flake8 --statistics ${PACKAGE} sandbox tests setup.py

pylint:
	pylint -j0 --rcfile=.pylintrc --reports=y ${PACKAGE} sandbox tests setup.py

mypy:
	mypy --install-types --non-interactive --no-strict-optional ${PACKAGE} sandbox tests

run-tox:
	tox --verbose --parallel all

test:
	PYTHONPATH=. pytest -v -rf --strict-markers \
		-p ${PACKAGE}.tester.plugins.fixtures \
		-p ${PACKAGE}.tester.plugins.startup \
		--cov=${PACKAGE} --cov-report=html \
		--cov-config .coveragerc \
		tests

test-coverage:
	PYTHONPATH=. pytest -v -rf --strict-markers \
		-p ${PACKAGE}.tester.plugins.fixtures \
		-p ${PACKAGE}.tester.plugins.startup \
		--junitxml=junit-report.xml \
		--cov=${PACKAGE} --cov-report=xml \
		--cov-config .coveragerc \
		tests

safety:
	safety check \
		-r ${REQ_PATH}/requirements.txt \
		-r ${REQ_PATH}/requirements-db.txt \
		-r ${REQ_PATH}/requirements-http.txt \
		-r ${REQ_PATH}/requirements-crypto.txt \
		-r ${REQ_PATH}/requirements-net.txt

liccheck:
	liccheck \
		--level CAUTIOUS \
		-r ${REQ_PATH}/requirements.txt \
		-r ${REQ_PATH}/requirements-db.txt \
		-r ${REQ_PATH}/requirements-http.txt \
		-r ${REQ_PATH}/requirements-crypto.txt \
		-r ${REQ_PATH}/requirements-net.txt

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
