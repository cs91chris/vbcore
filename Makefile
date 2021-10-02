PACKAGE=vbcore
LOG_LEVEL=DEBUG
REQ_PATH=requirements
COMPILE_OPTS=--no-emit-trusted-host --no-emit-index-url --build-isolation
CONFIRM=@( read -p "Are you sure?!? [Y/n]: " sure && case "$$sure" in [nN]) false;; *) true;; esac )

PIP_CONFIG_FILE=pip.conf
PYINSTALLER_OPTS=--log-level=${LOG_LEVEL} --collect-submodules ${PACKAGE} --add-data resources:resources --noconfirm --strip

all: clean lint clean-install-deps test

compile-deps:
	pip-compile ${COMPILE_OPTS} -o ${REQ_PATH}/requirements.txt ${REQ_PATH}/requirements.in
	pip-compile ${COMPILE_OPTS} -o ${REQ_PATH}/requirements-test.txt ${REQ_PATH}/requirements-test.in
	pip-compile ${COMPILE_OPTS} -o ${REQ_PATH}/requirements-dev.txt ${REQ_PATH}/requirements-dev.in

upgrade-deps:
	pip-compile --upgrade ${COMPILE_OPTS} -o ${REQ_PATH}/requirements.txt ${REQ_PATH}/requirements.in
	pip-compile --upgrade ${COMPILE_OPTS} -o ${REQ_PATH}/requirements-test.txt ${REQ_PATH}/requirements-test.in
	pip-compile --upgrade ${COMPILE_OPTS} -o ${REQ_PATH}/requirements-dev.txt ${REQ_PATH}/requirements-dev.in

install-deps:
	pip install -r ${REQ_PATH}/requirements.txt
	pip install -r ${REQ_PATH}/requirements-test.txt
	pip install -r ${REQ_PATH}/requirements-dev.txt

clean-install-deps:
	pip-sync ${REQ_PATH}/requirements*.txt

clean:
	find . -name '*.pyc' -prune -exec rm -rf {} \;
	find . -name '__pycache__' -prune -exec rm -rf {} \;
	find . -name '.pytest_cache' -prune -exec rm -rf {} \;

lint:
	@echo "---> running black ..."
	black -t py38 ${PACKAGE} tests setup.py
	@echo "---> running flake8 ..."
	flake8 --config=.flake8 ${PACKAGE} tests setup.py
	@echo "---> running pylint ..."
	pylint --rcfile=.pylintrc ${PACKAGE} tests setup.py
	@echo "---> running mypy ..."
	mypy --install-types --non-interactive --no-strict-optional ${PACKAGE} tests

test:
	pytest -v --cov=${PACKAGE} --cov-report=html --cov-config .coveragerc tests

build-cython:
	python setup.py bdist_wheel --cythonize

bump-build:
	bumpversion -n build --verbose
	${CONFIRM}
	bumpversion build --verbose

bump-release:
	bumpversion -n release --verbose
	${CONFIRM}
	bumpversion release --verbose

bump-major:
	bumpversion -n major --verbose
	${CONFIRM}
	bumpversion major --verbose

bump-minor:
	bumpversion -n minor --verbose
	${CONFIRM}
	bumpversion minor --verbose

bump-patch:
	bumpversion -n patch --verbose
	${CONFIRM}
	bumpversion patch --verbose
