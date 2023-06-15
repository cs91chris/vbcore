# {skeleton}

## First Setup

Setup custom git hooks:

```shell
git config core.hooksPath .git-hooks
```

<hr>

Setup a virtual env then install all dependencies:

```shell
python3.10 -m venv venv
. venv/bin/activate
pip install pip-tools
```

```shell
make compile-deps clean-install-deps
```

<hr>

Then run the pipeline in order to check that everything is correct

```shell
make run-tox
```

*See Makefile for extra commands...*

**NOTE**: make sure that the gitlab repo points to the correct ci config file.
The default is `.gitlab-ci.yml`, here it is `devops/gitlab-ci.yml`
