#!/bin/bash
set -e
LOCAL_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
ROOT_DIR=$( dirname "$(dirname "$LOCAL_DIR")")
cd "$ROOT_DIR"
set +x # double-check that x is unset
python setup.py sdist bdist_wheel --universal
cat > ~/.pypirc << EOF
[distutils]
index-servers=
    pypi
    testpypi

[testpypi]
repository = https://testpypi.python.org/pypi
username = nihlaeth
password = ${PYPI_PASSWORD}

[pypi]
repository = https://upload.pypi.org/legacy/
username = nihlaeth
password = ${PYPI_PASSWORD}
EOF
twine upload -r ${PYPI_REPOSITORY} dist/*
