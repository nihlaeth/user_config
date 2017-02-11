"""User config management."""
import sys
import collections
from pathlib import Path
import argparse
from pkg_resources import iter_entry_points
from appdirs import AppDirs

class MappingMixin(object):

    """Methods for emulating a mapping type."""

    def __getattr__(self, key):
        return self._data[key]

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        elif self._elements is None or key not in self._elements:
            self.__dict__[key] = value
        else:
            self._elements[key].validate(value)
            self._data[key] = value

    def __len__(self):
        return len(self._elements)

    def __getitem__(self, key):
        return self._dict['key']

    def __setitem__(self, key, value):
        if key not in self._elements:
            raise AttributeError(
                'no field with name {}'.format(key))
        self._elements[key].validate(value)
        self._data[key] = value

    def __iter__(self):
        return iter(self._data)

    def __reversed__(self):
        return reversed(self._data)

    def __contains__(self, item):
        return item in self._elements

    def keys(self):
        """Return a view of dictionary keys."""
        return self._data.keys()

    def values(self):
        """Return a view of dictionary values."""
        return self._data.values()

    def items(self):
        """Return a view of dictionary key, value pairs."""
        return self._data.items()

    def get(self, key, default):
        """Get items without risking a KeyError."""
        return self._data.get(key, default)

    def update(self, *args, **kwargs):
        """Update more than one key at a time."""
        # TODO: validate
        self._data.update(*args, **kwargs)

class ConfigElement(object):

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

    Attributes
    ----------
    element_name: str
        name of instance, provided by containing class
    type_: type
        python type of variable that this class represents

    Examples
    --------
    ..doctest::

        >>> TODO
    """
    element_name = None
    type_ = str

    def __init__(
            self,
            doc=None,
            default=None,
            required=True,
            short_name=None,
            long_name=None,
            validate=None):
        self.doc = doc
        self._default = default
        self.required = required
        if short_name is None or short_name.startswith('-'):
            self._short_name = short_name
        else:
            self._short_name = '-{}'.format(short_name)
        if long_name is None or long_name.startswith('--'):
            self._long_name = long_name
        else:
            self._long_name = '--{}'.format(long_name)
        self._validate = validate

        if self._default is not None:
            self.validate(self._default)

    def has_default(self):
        """Return True if element has a default value."""
        return self._default is not None

    def get_default(self):
        """Return default value."""
        return self._default

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
        name = []
        if self._short_name is not None:
            name.append(self._short_name)
        if self._long_name is not None:
            name.append(self._long_name)
        else:
            name.append("--{}".format(self.element_name))
        parser.add_argument(
            *name,
            action='store',
            #nargs=1,
            default=None,
            type=self.type_,
            choices=None,
            required=False,
            help=self.doc)

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
        None

        Returns
        -------
        None

        Examples
        --------
        ..doctest::

            >>> TODO
        """
        name = self.element_name if self._long_name is None else self._long_name[2:]
        if command_line_arguments[name] is None:
            return
        data[self.element_name] = command_line_arguments[name]

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

        Returns
        -------
        None

        Examples
        --------
        ..doctest::

            >>> TODO
        """
        if value is None:
            return
        if not isinstance(value, self.type_):
            raise InvalidData('expected a {}, not {}'.format(
                self.type_, value))
        if self._validate is not None:
            self._validate(value)

    def validate_data(self, data):
        """
        Validate data.

        Parameters
        ----------
        data: Dict
            data structure in which to find and validate our own element

        Raises
        ------
        InvalidData:
            if validation fails
        MissingData:
            if `self.required` is `True` and our value in `data`
            is `None`

        Returns
        -------
        None

        Examples
        --------
        ..doctest::

            >>> TODO
        """
        if self.required and data[self.element_name] is None:
            # none of the configuration locations provided a required
            # value, raise an error now
            raise MissingData(
                'no value was provided for required option {}'.format(
                    self.element_name))
        if data[self.element_name] is not None:
            self.validate(data[self.element_name])

class Section(ConfigElement, MappingMixin):

    """
    Named container that contains ConfigElements.

    Keyword Arguments
    -----------------
    doc: str, optional
        documentation for this option, defaults to None
    default: Any, optional
        IGNORED
    required: bool, optional
        MUST section be present? If no default is provided for any
        required content elements, this can result in a
        MissingData exception. to find out if an optional section
        is complete, see `self.incomplete_count`. Defaults to True
    short_name: str, optional
        IGNORED
    long_name: str, optional
        IGNORED
    validate: Callable[Any, None], optional
        additional validation function, defaults to None
    **content: ConfigElement, optional
        content of section

    Raises
    ------
    AttributeError:
        if content element is not a `ConfigElement`

    Attributes
    ----------
    incomplete_count: int
        Number of content elements which are required, but do not have a
        value. Useful for sections which are not marked as required, but
        do have required elements.

    Examples
    --------
    ..doctest::

        >>> TODO
    """

    incomplete_count = 0
    _elements = None
    _data = None

    def __init__(
            self,
            doc=None,
            default=None,
            required=True,
            short_name=None,
            long_name=None,
            validate=None,
            **content):
        self._elements = collections.OrderedDict()
        self._data = collections.OrderedDict()
        ConfigElement.__init__(
            self,
            doc=doc,
            required=required,
            short_name=short_name,
            long_name=long_name,
            validate=validate)
        for element in content:
            if not isinstance(content[element], ConfigElement):
                raise AttributeError(
                    '{} is not a ConfigElement'.format(element))
            content[element].element_name = element
            self._elements[element] = content[element]

    def has_default(self):
        """Return True because Section always has a default value."""
        return True

    def get_default(self):
        """Fetch and store default Section elements."""
        for element in self._elements:
            if self._elements[element].has_default():
                self._data[element] = self._elements[element].get_default()
            else:
                self._data[element] = None
        return self

    def get_elements(self):
        """Return elements and data."""
        return self._elements, self._data

    def construct_parser(self, parser):
        for element in self._elements:
            self._elements[element].construct_parser(parser)

    def extract_data_from_parser(self, command_line_arguments, _):
        for element in self._elements:
            self._elements[element].extract_data_from_parser(
                command_line_arguments, self._data)

    def validate(self, value):
        pass

    def validate_data(self, _):
        for element in self._elements:
            try:
                self._elements[element].validate_data(self._data)
            except MissingData:
                if not self.required:
                    self.incomplete_count += 1
                else:
                    raise

class StringOption(ConfigElement):

    """Configuration element with string value."""

    type_ = str

class IntegerOption(ConfigElement):

    """Configuration element with integer value."""

    type_ = int

class FloatOption(ConfigElement):

    """Configuration element with float value."""

    type_ = float

class BooleanOption(ConfigElement):

    """Configuration element with boolean value."""

    type_ = bool

def with_metaclass(meta, *bases):
    """
    Create a base class with a metaclass.

    Drops the middle class upon creation.
    Source: http://lucumr.pocoo.org/2013/5/21/porting-to-python-3-redux/

    Parameters
    ----------
    meta: type
        meta class or function
    *bases: object
        parents of class to be created

    Raises
    ------
    None

    Returns
    -------
    class of type `name`

    Examples
    --------
    ..doctest::

        >>> TODO
    """
    class MetaClass(meta):
        """Man-in-the-middle class."""
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, dictionary):
            if this_bases is None:
                return type.__new__(cls, name, (), dictionary)
            return meta(name, bases, dictionary)
    return MetaClass('temporary_class', None, {})

class ConfigMeta(type):

    """
    ORM-like magic for configuration class.

    Gather all `ConfigElement` attributes into `_elements` and
    get correct `_validate`, `_read` and `_writer` functions.

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
        if no appropriate `entry_point` could be found for `file_type`

    Examples
    --------
    ..doctest::

        >>> TODO
    """
    def __new__(mcs, cls_name, cls_parents, cls_attributes):
        reserved_names = [
            '_elements',
            '_extension',
            '_read',
            '_write',
            '_validate']
        new_attributes = {'_elements': collections.OrderedDict()}
        for attribute in cls_attributes:
            if attribute in reserved_names:
                raise AttributeError(
                    '{} is a reserved attribute for Config classes'.format(
                        attribute))
            elif isinstance(cls_attributes[attribute], ConfigElement):
                new_attributes['_elements'][attribute] = cls_attributes[attribute]
                new_attributes['_elements'][attribute].element_name = attribute
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
            else:
                new_attributes[attribute] = cls_attributes[attribute]
        return type.__new__(mcs, cls_name, cls_parents, new_attributes)

class InvalidConfigTree(Exception):

    """Inappropriate configuration tree for file type."""

class InvalidData(Exception):

    """User supplied invalid data for a configuration element."""

class MissingData(Exception):

    """An element marked as required is missing a value."""

class Config(with_metaclass(ConfigMeta, MappingMixin)):

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
    version: str, optional
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
    _data = None

    def __init__(self):
        if self.application is None:
            raise AttributeError(
                'application not set, please provide an application name')
        if self.author is None:
            raise AttributeError(
                'author not set, please provide an application author')
        self._data = collections.OrderedDict()
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
        user_path = Path(paths.user_config_dir).joinpath(
            "config.{}".format(self._extension))
        if user_path.is_file():
            self._read(user_path, self._elements, self._data)
        # construct a commandline parser
        parser = argparse.ArgumentParser(
            prog=self.application,
            description="{}\n\n{}\n{}\n{}".format(
                self.__doc__,
                "Command line arguments overwrite configuration found in:",
                user_path,
                global_path))
        parser.add_argument(
            '--generate-config',
            action='store_const',
            const=True,
            default=False,
            required=False,
            help="print a complete configuration file with current settings")
        for element in self._elements:
            self._elements[element].construct_parser(parser)
        command_line_arguments = vars(parser.parse_args())

        # check if we should print a configuration file
        if command_line_arguments['generate_config']:
            self._write(self._elements, self._data, self.__doc__)
            sys.exit(True)

        # put command line argument data into _data
        for element in self._elements:
            self._elements[element].extract_data_from_parser(
                command_line_arguments, self._data)
            # validate _data
            self._elements[element].validate_data(self._data)

    def __getattr__(self, name):
        return self._data[name]
