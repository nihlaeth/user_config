#!/bin/bash
set -ev
echo "check #1"
set +x # double-check that x is unset
echo "check #2"
$(which python) setup.py sdist bdist_wheel --universal
echo "check #3"
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
echo "check #4"
if [ "${TRAVIS_PYTHON_VERSION}" = "3.6" ]; then
    $(which twine) upload -r ${TWINE_REPOSITORY} dist/*
fi

# reset ownership so that we can stop using sudo
# sudo chown --changes --recursive $(whoami):$(id --group $(whoami)) .
# sudo chown --changes $(whoami):$(id --group $(whoami)) ~/.pypirc
