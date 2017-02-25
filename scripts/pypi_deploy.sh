#!/bin/bash
set -e
set +x # double-check that x is unset
python setup.py sdist bdist_wheel --universal
touch ~/.pypirc
#cat > .pypirc << EOF
#[distutils]
#index-servers=
#    pypi
#    testpypi
#
#[server-login]
#username = nihlaeth
#password = ${PYPI_PASSWORD}
#
#[testpypi]
#repository = https://testpypi.python.org/pypi
#
#[pypi]
#repository = https://upload.pypi.org/legacy/
#EOF
twine upload dist/*
