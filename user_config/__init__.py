"""User config management."""
from pathlib import Path
import argparse
from pkg_resources import iter_entry_points

class ConfigElement(object):

    """
    TODO

    TODO

    Raises
    ------
    TODO

    Attributes
    ----------
    : TODO
        TODO

    Examples
    --------
    ..doctest::

        >>> TODO
    """

    def __init__(self):
        pass

def config_meta(cls_name, cls_parents, cls_attributes):
    """
    ORM-like magic for configuration classes.

    Gather all ConfigElement attributes into _elements and
    get correct reader and writer functions.

    Parameters
    ----------
    cls_name: str
        class name
    cls_parents: Tuple[class]
        class parents
    cls_attributes: Dict
        class attributes

    Raises
    ------
    AttributeError:
        if class tries to overwrite a reserved attribute
    ImportError:
        if no appropriate entry_point could be found for file_type

    Returns
    -------
    class

    Examples
    --------
    ..doctest::

        >>> TODO
    """
    reserved_names = [
        '_elements',
        '_extension',
        '_read',
        '_write',
        '_validate']
    new_attributes = {'_elements': {}}
    for attribute in cls_attributes:
        if isinstance(cls_attributes[attribute], ConfigElement):
            new_attributes['_elements'][attribute] = cls_attributes[attribute]
            new_attributes['_elements'][attribute].name = attribute
        elif attribute == 'file_type':
            file_types = {}
            for entry_point in iter_entry_points('user_config.file_type'):
                # TODO: deal with duplicate entry point names
                file_types[entry_point.name] = entry_point
            if cls_attributes[attribute] not in file_types:
                raise ImportError(
                    'no entry point found for file type {}'.format(
                        cls_attributes[attribute]))
            extension = file_types[cls_attributes[attribute]].load()()
            new_attributes['_extension'] = extension['extension']
            new_attributes['_read'] = extension['read']
            new_attributes['_write'] = extension['write']
            new_attributes['_validate'] = extension['validate']
        elif attribute in reserved_names:
            raise AttributeError(
                '{} is a reserved attribute for Config classes'.format(
                    attribute))
        else:
            new_attributes[attribute] = cls_attributes[attribute]
    return type(cls_name, cls_parents, new_attributes)

class InvalidConfigTree(Exception):

    """Inappropriate configuration tree for file type."""

class InvalidData(Exception):

    """User supplied invalid data for a configuration element."""

class MissingData(Exception):

    """An element marked as required is missing a value."""

class Config(metaclass=config_meta):

    """
    Base class for application configuration.

    TODO

    Raises
    ------
    AttributeError:
        if application is not set
    InvalidConfigTree:
        if configuration tree is inappropriate for file_type
    InvalidData:
        if user supplied invalid data for a configuration element
    MissingData:
        if an element marked as required has no value

    Attributes
    ----------
    file_type: str
        file type to use for configuration files
    application: str
        application name

    Examples
    --------
    ..doctest::

        >>> TODO
    """

    file_type = "ini"
    application = None

    def __init__(self):
        if self.application is None:
            raise AttributeError(
                'application not set, please provide an application name')
        self._data = {}
        # validate _elements
        self._validate(self._elements)
        # populate _data
        for element in self._elements:
            if self._elements[element].has_default:
                self._data[element] = self._elements[element].get_default()
            else:
                self._data[element] = None
        # read global config
        global_path = Path('/etc').joinpath("{}{}".format(
            self.application, self._extension))
        if not global_path.is_file():
            alternate_global_path = global_path
            global_path = Path('/etc').joinpath(self.application).joinpath(
                "config{}".format(self._extension))
        if global_path.is_file():
            self._read(global_path, self._elements, self._data)
        # read user config
        user_path = Path().home().joinpath(".{}{}".format(
            self.application, self._extension))
        if not user_path.is_file():
            alternate_user_path = user_path
            user_path = Path().home().joinpath(".config").joinpath(
                self.application).joinpath("config{}".format(self._extension))
        if user_path.is_file():
            self._read(user_path, self._elements, self._data)
        # construct a commandline parser
        parser = argparse.ArgumentParser(
            prog=self._application,
            description="{}\n\n{}\n{}\n{}".format(
                self.__doc__,
                "Command line arguments overwrite configuration found in:",
                user_path if alternate_user_path is None else alternate_user_path,
                global_path if alternate_global_path is None else alternate_global_path))
        for element in self._elements:
            self._elements[element].construct_parser(parser)
        # put command line argument data into _data
        command_line_arguments = parser.parse_args()
        for element in self._elements:
            self._elements[element].extract_data_from_parser(
                command_line_arguments, self._data)
            # validate _data
            self._elements[element].validate_data(self._data)
