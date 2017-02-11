"""ini configuration file format."""
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
from user_config import Section, InvalidConfigTree

def ini_validate(_, elements):
    """
    Make sure element tree is suitable for ini files.

    Parameters
    ----------
    elements: Dict[ConfigElement]
        element tree

    Raises
    ------
    InvalidConfigTree:
        if the config tree is inappropriate for ini files

    Returns
    -------
    None

    Examples
    --------
    ..doctest::

        >>> TODO
    """
    for element in elements:
        if not isinstance(elements[element], Section):
            raise InvalidConfigTree(
                'root element can only contain Section elements for ini files')
        sub_elements, _ = elements[element].get_elements()
        for sub_element in sub_elements:
            if isinstance(sub_elements[sub_element], Section):
                raise InvalidConfigTree(
                    'nested sections are not supported for ini files')

def ini_read(_, path, elements, data):
    """
    Read ini configuration file and populate `data`.

    Parameters
    ----------
    path: pathlib.Path
        path to configuration file
    elements: Dict[ConfigElement]
        configuration element tree
    data: Dict
        data tree

    Raises
    ------
    TODO

    Returns
    -------
    TODO

    Examples
    --------
    ..doctest::

        >>> TODO
    """
    config = configparser.ConfigParser()
    config.read(str(path))
    for section in elements:
        keys, values = elements[section].get_elements()
        for key in keys:
            try:
                if keys[key].type_ == bool:
                    values[key] = config.getboolean(section, key)
                else:
                    values[key] = keys[key].type_(config.get(section, key))
            except configparser.NoOptionError:
                pass
            except configparser.NoSectionError:
                pass

def ini_write(_):
    """Write default ini file."""
    pass

def register_extension():
    """
    Register ini file format functions with user_config.

    Returns
    -------
    Dict

    Examples
    --------
    ..doctest::

        >>> TODO
    """
    return {
        'extension': 'cfg',
        'read': ini_read,
        'write': ini_write,
        'validate': ini_validate}
