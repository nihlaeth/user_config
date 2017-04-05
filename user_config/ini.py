"""ini configuration file format."""
import collections
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
    _: user_config.Config
        IGNORED
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
    if not isinstance(elements, collections.OrderedDict):
        raise InvalidConfigTree(
            'elements should be an OrderedDict, not {}'.format(elements))
    for element in elements:
        if not isinstance(elements[element], Section):
            raise InvalidConfigTree(
                'root element can only contain Section elements for ini files')
        sub_elements = elements[element].get_elements()
        for sub_element in sub_elements:
            if isinstance(sub_elements[sub_element], Section):
                raise InvalidConfigTree(
                    'nested sections are not supported for ini files')
            if sub_elements[sub_element].type_ not in (
                    str, int, float, bool, list):
                raise InvalidConfigTree(
                    'unsupported data type {}'.format(
                        sub_elements[sub_element].type_))

def ini_read(_, path, elements):
    """
    Read ini configuration file and populate `data`.

    Parameters
    ----------
    _: user_config.Config
        IGNORED
    path: pathlib.Path
        path to configuration file
    elements: Dict[ConfigElement]
        configuration element tree

    Raises
    ------
    None

    Returns
    -------
    None

    Examples
    --------
    ..doctest::

        >>> TODO
    """
    config = configparser.ConfigParser()
    config.read(str(path))
    for section in elements:
        keys = elements[section].get_elements()
        for key in keys:
            try:
                if keys[key].type_ == bool:
                    keys[key].set_value(config.getboolean(section, key))
                elif keys[key].type_ == list:
                    value = config.get(section, key).split('\n')
                    if len(value) == 1 and value[0] == '':
                        continue
                    result = []
                    for item in value:
                        item = item.lstrip()
                        if not item.startswith("- "):
                            raise ValueError(
                                '{} is not a valid ini list'.format(
                                    config.get(section, key)))
                        result.append(item[2:])
                    keys[key].set_value(result)
                elif keys[key].type_ == str:
                    value = str(config.get(section, key))
                    if value != '':
                        keys[key].set_value(value)
                elif keys[key].type_ == int or keys[key].type_ == float:
                    keys[key].set_value(
                        keys[key].type_(config.get(section, key)))
            except ValueError:
                # if the value is empty string, not defined, ignore
                if config.get(section, key) != '':
                    raise
            except configparser.NoOptionError:
                pass
            except configparser.NoSectionError:
                pass

def _print_item(key, item, value):
    """Print single key value pair."""
    # print docstring
    if item.doc is not None:
        doc_string = item.doc.split('\n')
        for line in doc_string:
            print("## {}".format(line))

    # TODO: display data type
    # print default
    if item.has_default():
        # handle multiline strings
        if item.type_ == list:
            lines = ['- {}'.format(thing) for thing in item.get_default()]
        else:
            lines = str(item.get_default()).split('\n')
        print("# {} = {}".format(key, lines[0]))
        if len(lines) > 1:
            for line in lines[1:]:
                print("#     {}".format(line))
    else:
        if item.required:
            print("## REQUIRED")
        print("# {} = ".format(key))

    # print current value
    if value is None and item.required:
        print("{} = ".format(key))
    elif value is not None and value != item.get_default():
        # handle multiline strings
        if item.type_ == list:
            lines = ['- {}'.format(thing) for thing in value]
        else:
            lines = str(value).split('\n')
        print("{} = {}".format(key, lines[0]))
        if len(lines) > 1:
            for line in lines[1:]:
                print("    {}".format(line))
    print("")

def ini_write(_, elements, doc):
    """
    Print default ini file.

    This includes data already set in the existing configuration files.

    Parameters
    ----------
    _: user_config.Config
        IGNORED
    elements: Dict[ConfigElement]
        configuration element tree
    doc: Option[str]
        `Config` class docstring

    Raises
    ------
    None

    Returns
    -------
    None

    Examples
    --------
    ..doctest::

        >>> TODO
    """
    # print config class docstring
    if doc is not None:
        doc_string = doc.split('\n')
        for line in doc_string:
            print("## {}".format(line))
        print("")

    for section in elements:
        print("[{}]".format(section))
        # print docstring and optional status
        if elements[section].doc is not None:
            doc_string = elements[section].doc.split('\n')
            for line in doc_string:
                print("## {}".format(line))
        if not elements[section].required:
            print("## OPTIONAL_SECTION")
        if elements[section].doc is not None or not elements[section].required:
            print("")

        keys = elements[section].get_elements()
        for key in keys:
            _print_item(key, keys[key], keys[key].get_value())
        print("")

def register_extension():
    """
    Register ini file format functions with `user_config`.

    Returns
    -------
    Dict

    Examples
    --------
    ..doctest::

        >>> register_extension()
        {'read': <function ini_read at 0x...>, 'write': <function ini_write at 0x...>, 'validate': <function ini_validate at 0x...>, 'extension': 'cfg'}
    """
    return {
        'extension': 'cfg',
        'read': ini_read,
        'write': ini_write,
        'validate': ini_validate}
