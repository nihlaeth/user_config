#!/bin/bash
set -ev
# set +x # double-check that x is unset
$(which python) setup.py sdist bdist_wheel --universal
cat > ~/.pypirc << _EOF_
[distutils]
index-servers=
    pypi
    testpypi

[testpypi]
repository = https://testpypi.python.org/pypi
username = ${TWINE_USERNAME}
password = ${TWINE_PASSWORD}

[pypi]
repository = https://upload.pypi.org/legacy/
username = ${TWINE_USERNAME}
password = ${TWINE_PASSWORD}
_EOF_
if [ "${TRAVIS_PYTHON_VERSION}" = "3.6" ]; then
    $(which twine) upload -r testpypi --skip-existing dist/*
    if [ "${TRAVIS_TAG}" != "" ]; then
        $(which twine) upload -r pypi --skip-existing dist/*
    fi
fi
