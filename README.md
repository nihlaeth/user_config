# user_config
manage user configuration for python projects

## Fallback order
1. command line arguments
2. user config files in `~/.<app>(rc|.<extension>)` or `~/.config/<app>/config[.<extension>]`
3. global config files in `/etc/<app>[.<extension>]` or `/etc/<app>/config[.<extension>]`
4. default values

## Config format
Supported out of the box: ini

Other config formats can be supported via plug-ins.

## Planned features
* support for python version 2
* Windows support
* support for multi file configuration
* command line option to generate fully commented config file with default values
