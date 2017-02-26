#!/bin/bash
echo 1
set -ev
set +x # double-check that x is unset
echo 2
$(which python) setup.py sdist bdist_wheel --universal
echo 3
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
echo 4
$(which twine) upload -r ${TWINE_REPOSITORY} dist/*

# reset ownership so that we can stop using sudo
# sudo chown --changes --recursive $(whoami):$(id --group $(whoami)) .
# sudo chown --changes $(whoami):$(id --group $(whoami)) ~/.pypirc
