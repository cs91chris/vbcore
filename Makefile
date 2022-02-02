PACKAGE=vbcore
LOG_LEVEL=DEBUG
REQ_PATH=requirements
export PIP_CONFIG_FILE=pip.conf
COMPILE_OPTS=--no-emit-trusted-host --no-emit-index-url --build-isolation

define bump_version
	bumpversion -n $(1) --verbose
	@( read -p "Are you sure?!? [Y/n]: " sure && case "$$sure" in [nN]) false;; *) true;; esac )
	bumpversion $(1) --verbose
endef

define copy_requirements
	cp ${REQ_PATH}/requirements-$(1).txt ${SERVICE_PATH}/$(2)/requirements.txt
endef

define req_compile
	pip-compile $(2) ${COMPILE_OPTS} -o ${REQ_PATH}/$(1).txt ${REQ_PATH}/$(1).in
endef


all: clean lint clean-install-deps test safety

compile-deps:
	$(call req_compile,requirements)
	$(call req_compile,requirements-all)
	$(call req_compile,requirements-test)
	$(call req_compile,requirements-dev)

upgrade-deps:
	$(call req_compile,requirements,--upgrade)
	$(call req_compile,requirements-all,--upgrade)
	$(call req_compile,requirements-test,--upgrade)
	$(call req_compile,requirements-dev,--upgrade)

install-deps:
	pip install -r ${REQ_PATH}/requirements.txt
	pip install -r ${REQ_PATH}/requirements-all.txt
	pip install -r ${REQ_PATH}/requirements-test.txt
	pip install -r ${REQ_PATH}/requirements-dev.txt

clean-install-deps:
	pip-sync ${REQ_PATH}/requirements*.txt

clean:
	find . -name '*.pyc' -prune -exec rm -rf {} \;
	find . -name '__pycache__' -prune -exec rm -rf {} \;
	find . -name '.pytest_cache' -prune -exec rm -rf {} \;
	find ${PACKAGE} -name ".mypy_cache" -prune -exec rm -rf {} \;

lint:
	black -t py38 ${PACKAGE} sandbox tests setup.py
	flake8 --config=.flake8 ${PACKAGE} sandbox tests setup.py --statistics
	pylint --rcfile=.pylintrc ${PACKAGE} sandbox tests setup.py
	mypy --install-types --non-interactive --no-strict-optional ${PACKAGE} sandbox tests

test:
	PYTHONPATH=. pytest -v -rf --strict-markers \
		-p ${PACKAGE}.tester.plugins.fixtures \
		-p ${PACKAGE}.tester.plugins.startup \
		--cov=${PACKAGE} --cov-report=html \
		--cov-config .coveragerc \
		tests

safety:
	safety check \
		-r ${REQ_PATH}/requirements.txt \
		-r ${REQ_PATH}/requirements-all.txt

image-publish:
	docker build --target ${PACKAGE}-38 -t voidbrain/${PACKAGE}-38:$${VERSION:-latest} .
	docker push voidbrain/${PACKAGE}-38:$${VERSION:-latest}

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
