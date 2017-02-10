"""User config management."""
from abc import ABCMeta, abstractmethod
from pathlib import Path
import argparse
from pkg_resources import iter_entry_points
from appdirs import AppDirs

class ConfigElement(object, metaclass=ABCMeta):

    """
    Base class for configuration elements.

    Keyword Arguments
    -----------------
    doc: str, optional
        documentation for this option, defaults to None
    default: Any, optional
        fallback value, defaults to None
    required: bool, optional
        MUST a value be present? If no default is provided, this can
        result in a MissingData exception. Defaults to True
    short_name: str, optional
        short name for use with command line arguments, defaults to None
    long_name: str, optional
        overwrite default name for command line arguments, defaults to None
    validate: Callable[Any, None], optional
        additional validation function, defaults to None

    Raises
    ------
    InvalidArgument:
        if default value does not pass validation

    Examples
    --------
    ..doctest::

        >>> TODO
    """

    def __init__(
            self,
            doc=None,
            default=None,
            required=True,
            short_name=None,
            long_name=None,
            validate=None):
        self._doc = doc
        self._default = default
        self._required = required
        self._short_name = short_name
        self._long_name = long_name
        self._validate = validate

        if self._default is not None:
            self.validate(self._default)

    def has_default(self):
        """Return True if element has a default value."""
        return self._default is not None

    @abstractmethod
    def construct_parser(self, parser):
        """
        Add self to parser.

        Parameters
        ----------
        parser: argparse.ArgumentParser
            the argument parser to add an option to

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
        pass

    @abstractmethod
    def extract_data_from_parser(self, command_line_arguments, data):
        """
        Get value from parser.

        Parameters
        ----------
        command_line_arguments: argparse.Namespace
            parsed arguments
        data: Dict
            dictionary to put values in (assumes tree structure is
            already in place)

        Raises
        ------
        InvalidData:
            if user provides invalid value

        Returns
        -------
        None

        Examples
        --------
        ..doctest::

            >>> TODO
        """
        pass

    @abstractmethod
    def validate(self, value):
        """
        Validate individual value.

        Parameters
        ----------
        value: Any
            to be validated

        Raises
        ------
        InvalidData:
            if validation fails
        MissingData:
            if `self._required` is `True` and `value` is `None`

        Returns
        -------
        None

        Examples
        --------
        ..doctest::

            >>> TODO
        """
        if self._validate is not None:
            self._validate(value)

    @abstractmethod
    def validate_data(self, data):
        """
        Validate data.

        Parameters
        ----------
        data: Dict
            data tree in which to find and validate our own element

        Raises
        ------
        InvalidData:
            if validation fails
        MissingData:
            if `self._required` is `True` and our value in `data`
            is `None`

        Returns
        -------
        None

        Examples
        --------
        ..doctest::

            >>> TODO
        """
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

    Raises
    ------
    AttributeError:
        if `application` or `author` is not set
    InvalidConfigTree:
        if configuration tree is inappropriate for `file_type`
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
    author: str
        application author
    version: str
        application version (set if your configuration is version
        dependent)

    Examples
    --------
    ..doctest::

        >>> TODO
    """

    file_type = "ini"
    application = None
    author = None
    version = None

    def __init__(self):
        if self.application is None:
            raise AttributeError(
                'application not set, please provide an application name')
        if self.author is None:
            raise AttributeError(
                'author not set, please provide an application author')
        self._data = {}
        # validate _elements
        self._validate(self._elements)
        # populate _data
        for element in self._elements:
            if self._elements[element].has_default():
                self._data[element] = self._elements[element].get_default()
            else:
                self._data[element] = None
        # read global config
        paths = AppDirs(self.application, self.author, self.version)
        global_path = Path(paths.site_config_dir).joinpath(
            "config.{}".format(self._extension))
        if global_path.is_file():
            self._read(global_path, self._elements, self._data)
        # read user config
        user_path = Path(paths.user_data_dir).joinpath(
            "config.{}".format(self._extension))
        if user_path.is_file():
            self._read(user_path, self._elements, self._data)
        # construct a commandline parser
        parser = argparse.ArgumentParser(
            prog=self._application,
            description="{}\n\n{}\n{}\n{}".format(
                self.__doc__,
                "Command line arguments overwrite configuration found in:",
                user_path,
                global_path))
        for element in self._elements:
            self._elements[element].construct_parser(parser)
        # put command line argument data into _data
        command_line_arguments = parser.parse_args()
        for element in self._elements:
            self._elements[element].extract_data_from_parser(
                command_line_arguments, self._data)
            # validate _data
            self._elements[element].validate_data(self._data)
