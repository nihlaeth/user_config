.. user_config documentation master file, created by
   sphinx-quickstart on Sat Feb 11 15:39:42 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to user_config's documentation!
=======================================
manage user configuration for python projects

Contents:

.. toctree::
   :maxdepth: 2

   modules



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

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
* python 2.7 or new (python 3.6 supported)
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
        general = Section(
            name=StringOption(
                doc="your name",
                default="unknown person"),
            age=IntegerOption(
                doc="your age",
                required=True))
        address = Section(
            street=StringOption(
                doc="street including house number",
                required=True),
            city=StringOption(required=True),
            required=False,
            doc="shipping address")

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
      File "examples/simple_example.py", line 26, in <module>
        CONFIG = MyConfig()
      File "/git/user_config/user_config/user_config/__init__.py", line 541, in __init__
        self._elements[element].validate_data(self._data)
      File "/git/user_config/user_config/user_config/__init__.py", line 322, in validate_data
        self._elements[element].validate_data(self._data)
      File "/git/user_config/user_config/user_config/__init__.py", line 216, in validate_data
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

    [address]
    ## shipping address
    ## OPTIONAL_SECTION

    ## REQUIRED
    # city = 
    city = 

    ## street including house number
    ## REQUIRED
    # street = 
    street = 


    [general]
    ## your age
    ## REQUIRED
    # age = 
    age = 

    ## your name
    # name = unknown person

Planned features
================
* support for multi file configuration
* multi matching sections / wildcard sections
* yaml config format
* json config format
* hook for overwriting config from database or other storage function
