#!/bin/bash
set -e
set +x # double-check that x is unset
python setup.py sdist bdist_wheel --universal
cat > .pypirc << EOF
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
twine upload --config-file ./.pypirc -r ${PYPI_REPOSITORY} dist/*
