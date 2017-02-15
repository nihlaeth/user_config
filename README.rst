user_config
===========
Manage user configuration for python projects.

For easy and well-documented user-defined configuration.

Links
=====
* home: https://github.com/nihlaeth/user_config
* pypi: https://pypi.python.org/pypi/user-config
* documentation: http://user-config.readthedocs.io/en/latest/

Badges
======
* .. image:: https://readthedocs.org/projects/user-config/badge/?version=latest
        :target: http://user-config.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
* .. image:: https://travis-ci.org/nihlaeth/user_config.svg?branch=master
        :target: https://travis-ci.org/nihlaeth/user_config
* .. image:: https://api.codacy.com/project/badge/Grade/bd13a0474ea44c8e8a95e10ef4d89585
        :target: https://www.codacy.com/app/nihlaeth/user_config?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=nihlaeth/user_config&amp;utm_campaign=Badge_Grade
* .. image:: https://api.codacy.com/project/badge/Coverage/bd13a0474ea44c8e8a95e10ef4d89585
        :target: https://www.codacy.com/app/nihlaeth/user_config?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=nihlaeth/user_config&amp;utm_campaign=Badge_Coverage

Fallback order
==============
1. command line arguments
2. user config files in ``~/.config/<app>/config.<extension>``
3. global config files in ``/etc/xdg/<app>/config.<extension>``
4. default values

For directories on operating systems than linux, see: https://github.com/ActiveState/appdirs

Config format
=============
Supported out of the box: ini

Other config formats can be supported via plug-ins.

Requirements
============
* Linux, or Os X, or Windows (but not Windows Vista)
* python 2.7 or newer (python 3.6 supported)
* relatively new versions of setuptools and pip (version requirement to follow)

Examples
========

Simple configuration example
----------------------------

.. code-block:: python

    """Usage example for user_config."""
    from user_config import Config, Section, StringOption, IntegerOption

    class MyConfig(Config):

        """This will be displayed in the configuration documentation."""

        application = "my_application"
        author = "me"

        class GeneralSection(Section):
            """General information."""
            name = StringOption(
                doc="your name",
                default="unknown person")
            age = IntegerOption(
                doc="your age",
                required=True)
        general = GeneralSection()
        class AddressSection(Section):
            """shipping address"""
            street = StringOption(
                doc="street including house number",
                required=True)
            city = StringOption(required=True)
        address = AddressSection(required=False)

    if __name__ == "__main__":
        CONFIG = MyConfig()
        print("hello there, {}!".format(CONFIG.general.name))

Command line help text:

.. code-block:: shell

    $ python examples/simple_example.py -h
    usage: my_application [-h] [--generate-config] [--city CITY] [--street STREET]
                          [--age AGE] [--name NAME]

    This will be displayed in the configuration documentation. Command line
    arguments overwrite configuration found in:
    /root/.config/my_application/config.cfg /etc/xdg/my_application/config.cfg

    optional arguments:
      -h, --help         show this help message and exit
      --generate-config  print a complete configuration file with current settings
      --city CITY
      --street STREET    street including house number
      --age AGE          your age
      --name NAME        your name

Command line use with default value:

.. code-block:: shell

    $ python examples/simple_example.py --age 211
    hello there, unknown person!

Command line use without required value:

.. code-block:: shell

    $ python examples/simple_example.py
    Traceback (most recent call last):
      File "examples/simple_example.py", line 29, in <module>
        CONFIG = MyConfig()
      File "/git/user_config/user_config/user_config/__init__.py", line 622, in __init__
        self._elements[element].validate_data(self._data)
      File "/git/user_config/user_config/user_config/__init__.py", line 464, in validate_data
        self._elements[element].validate_data(self._data)
      File "/git/user_config/user_config/user_config/__init__.py", line 380, in validate_data
        self.element_name))
    user_config.MissingData: no value was provided for required option age

Command line use:

.. code-block:: shell

    $ python examples/simple_example.py --age 211 --name mystery_user
    hello there, mystery_user!

Generate configuration file:

.. code-block:: shell

    $ python examples/simple_example.py --generate-config
    ## This will be displayed in the configuration documentation.

    [general]
    ## General information.

    ## your name
    # name = unknown person
    name = tamara

    ## your age
    ## REQUIRED
    # age = 
    age = 


    [address]
    ## shipping address
    ## OPTIONAL_SECTION

    ## street including house number
    ## REQUIRED
    # street = 
    street = 

    ## REQUIRED
    # city = 
    city = 


Documentation
=============

.. code-block:: shell

    $ pip install -e ".[doc]"
    $ python setup.py build_sphinx

Testing
=======

* pytest
* pytest-cov
* coverage
* codacy-coverage

.. code-block:: shell

    $ python -m pytest --cov=user_config --cov-report xml

Planned features
================
* multi matching sections / wildcard sections
* yaml config format
* json config format
* hook for overwriting config from database or other storage function
