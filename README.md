# user_config
manage user configuration for python projects

## Fallback order
1. command line arguments
2. user config files in `~/.config/<app>/config.<extension>`
3. global config files in `/etc/xdg/<app>/config.<extension>`
4. default values

For directories on operating systems than linux, see: https://github.com/ActiveState/appdirs

## Config format
Supported out of the box: ini

Other config formats can be supported via plug-ins.

## Requirements
* Linux, or Os X, or Windows (but not Windows Vista)
* python 2.7 or new (python 3.6 supported)
* relatively new versions of setuptools and pip (version requirement to follow)

## Planned features
* support for multi file configuration
* command line option to generate fully commented config file with default values
* yaml config format
* json config format
