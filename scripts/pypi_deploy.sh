#!/bin/bash
set -e
set +x # double-check that x is unset
python setup.py sdist bdist_wheel --universal
cat > ~/.pypirc << _EOF_
[testpypi]
repository = https://testpypi.python.org/pypi
username = ${TWINE_USERNAME}
password = ${TWINE_PASSWORD}

[pypi]
repository = https://upload.pypi.org/legacy/
username = ${TWINE_USERNAME}
password = ${TWINE_PASSWORD}
_EOF_
twine upload -r ${TWINE_REPOSITORY} dist/*
