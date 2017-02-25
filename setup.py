"""Installation script for user_config."""
# pylint: disable=wrong-import-position
import sys
from pkg_resources import get_distribution, VersionConflict
try:
    get_distribution('setuptools>=24.2.1')
except VersionConflict:
    print("setuptools version 24.2.1 required, please upgrade!")
    sys.exit(False)
from setuptools import setup, find_packages, Command

class Doctest(Command):

    """Run sphinx doctests."""

    description = 'Run doctests with Sphinx'
    user_options = []
    target = 'doctest'
    output_dir = '.doc/build'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sphinx.application import Sphinx
        sph = Sphinx('./doc/source', # source directory
                     './doc/source', # directory containing conf.py
                     self.output_dir, # output directory
                     './doc/build/doctrees', # doctree directory
                     self.target) # finally, specify the doctest builder'
        sph.build()

with open('README.rst', 'r') as readme:
    LONG_DESCRIPTION = readme.read()

setup(
    name='user_config',
    description='manage user configuration for python packages',
    long_description=LONG_DESCRIPTION,
    author='nihlaeth',
    author_email='info@nihlaeth.nl',
    url='https://github.com/nihlaeth/user_config',
    license='GPLv3',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*',
    packages=find_packages(),
    setup_requires=['pytest-runner', 'vcversioner'],
    vcversioner={'version_file': 'VERSION'},
    tests_require=['pytest'],
    install_requires=['appdirs>=1.4'],
    extras_require={
        ':python_version <= "3.3"': ['pathlib'],
        'deploy': [
            'pytest',
            'coverage',
            'pytest-cov',
            'codacy-coverage',
            'twine>=1.8.1',
            'wheel'],
        'doctest': ['sphinx>=1.3.1'],
        'doc': [
            'sphinx>=1.3.1',
            'sphinx_rtd_theme',
            'sphinx-pypi-upload',
            'collective.checkdocs'],
    },
    cmdclass={'doctest': Doctest},
    entry_points={
        'user_config.file_type': [
            'ini = user_config.ini:register_extension']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Utilities'],
    keywords="configuration config documentation ui ini",
    )
