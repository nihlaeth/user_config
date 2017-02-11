"""Installation script for user_config."""
from setuptools import setup, find_packages

setup(
    name='user_config',
    version='1.0',
    description='manage user configuration for Python packages',
    author='nihlaeth',
    author_email='info@nihlaeth.nl',
    python_requires='>=2.7',
    packages=find_packages(),
    install_requires=['appdirs>=1.4', 'pathlib;python_version<"3.3"'],
    entry_points={
        'user_config.file_type': [
            'ini = user_config.ini:register_extension']},
    )
