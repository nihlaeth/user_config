"""User config management."""
import sys
import collections
from pathlib import Path
import argparse
from pkg_resources import iter_entry_points
from appdirs import AppDirs

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
        fields = {}
        for attribute in cls_attributes:
            if attribute in reserved_names:
                raise AttributeError(
                    '{} is a reserved attribute for Config classes'.format(
                        attribute))
            elif isinstance(cls_attributes[attribute], ConfigElement):
                fields[attribute] = cls_attributes[attribute]
                fields[attribute].element_name = attribute
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
        for attribute in sorted(
                fields, key=lambda name: fields[name].creation_counter):
            new_attributes['_elements'][attribute] = fields[attribute]
        return type.__new__(mcs, cls_name, cls_parents, new_attributes)

class MappingMixin(object):

    """Methods for emulating a mapping type."""

    def __getattr__(self, key):
        if isinstance(self._elements[key], MappingMixin):
            return self._elements[key]
        return self._elements[key].get_value()

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        elif self._elements is None or key not in self._elements:
            self.__dict__[key] = value
        else:
            self._elements[key].set_value(value)

    def __len__(self):
        return len(self._elements)

    def __getitem__(self, key):
        if isinstance(self._elements[key], MappingMixin):
            return self._elements[key]
        return self._elements[key].get_value()

    def __setitem__(self, key, value):
        if key not in self._elements:
            raise AttributeError(
                'no field with name {}'.format(key))
        self._elements[key].set_value(value)

    def __iter__(self):
        return iter(self._elements)

    def __reversed__(self):
        return reversed(self._elements)

    def __contains__(self, item):
        return item in self._elements

    def keys(self):
        """Return a view of dictionary keys."""
        return self._elements.keys()

    def values(self):
        """Return a view of dictionary values."""
        return self._elements.values()

    def items(self):
        """Return a view of dictionary key, value pairs."""
        return self._elements.items()

    def get(self, key, default):
        """Get items without risking a KeyError."""
        if key not in self._elements:
            return default
        else:
            if isinstance(self._elements[key], MappingMixin):
                return self._elements[key]
            return self._elements[key].get_value()

    def update(self, *args, **kwargs):
        """Update more than one key at a time."""
        # TODO: validate
        # self._elements.update(*args, **kwargs)
        raise NotImplementedError

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
    InvalidData:
        if default value does not pass validation

    Attributes
    ----------
    creation_counter: int
        global count of config elements, used to maintain field order
    element_name: str
        name of instance, provided by containing class
    type_: type
        python type of variable that this class represents
    action: str
        action for argparse

    Examples
    --------
    ..doctest::

        >>> TODO
    """
    creation_counter = 0
    element_name = None
    type_ = str
    action = 'store'
    _value = None

    def __init__(
            self,
            doc=None,
            default=None,
            required=True,
            short_name=None,
            long_name=None,
            validate=None):
        # Store the creation index in the instance "creation_counter"
        self.creation_counter = ConfigElement.creation_counter
        ConfigElement.creation_counter += 1
        self.doc = doc
        self._default = default
        self._value = default
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

    def get_value(self):
        """Return current option value."""
        return self._value

    def set_value(self, value):
        """Validate and store value."""
        self.validate(value)
        self._value = value

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
            action=self.action,
            #nargs=1,
            default=None,
            type=self.type_ if self.action == 'store' else self.subtype,
            choices=None,
            required=False,
            help=self.doc)

    def extract_data_from_parser(self, command_line_arguments):
        """
        Get value from parser.

        Parameters
        ----------
        command_line_arguments: argparse.Namespace
            parsed arguments

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
        self._value = command_line_arguments[name]

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

    def validate_data(self):
        """
        Validate data.

        Raises
        ------
        InvalidData:
            if validation fails
        MissingData:
            if `self.required` is `True` and our value is `None`

        Returns
        -------
        None

        Examples
        --------
        ..doctest::

            >>> TODO
        """
        if self.required and self._value is None:
            # none of the configuration locations provided a required
            # value, raise an error now
            raise MissingData(
                'no value was provided for required option {}'.format(
                    self.element_name))
        if self._value is not None:
            self.validate(self._value)

class StringListOption(ConfigElement):

    """
    Configuration element with list value.

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
    additive: bool, optional
        whether to add all found lists together instead of overwrite
        them, defaults to False

    Raises
    ------
    InvalidData:
        if default value does not pass validation

    Attributes
    ----------
    creation_counter: int
        global count of config elements, used to maintain field order
    element_name: str
        name of instance, provided by containing class
    type_: type
        python type of variable that this class represents
    subtype: type
        python type of list items
    action: str
        action for argparse

    Examples
    --------
    ..doctest::

        >>> TODO
    """

    type_ = list
    subtype = str
    action = 'append'

    def __init__(
            self,
            doc=None,
            default=None,
            required=True,
            short_name=None,
            long_name=None,
            validate=None,
            additive=False):
        ConfigElement.__init__(
            self,
            doc=doc,
            default=default,
            required=required,
            short_name=short_name,
            long_name=long_name,
            validate=validate)
        self._additive = additive

    def _merge_value(self, value):
        for item in value:
            if item not in self._value:
                self._value.append(item)

    def set_value(self, value):
        self.validate(value)
        if self._additive and self._value is not None and value is not None:
            self._merge_value(value)
        else:
            self._value = value

    def extract_data_from_parser(self, command_line_arguments):
        print(command_line_arguments)
        name = self.element_name if self._long_name is None else self._long_name[2:]
        if command_line_arguments[name] is None:
            return
        if self._additive and self._value is not None:
            self._merge_value(command_line_arguments[name])
        else:
            self._value = command_line_arguments[name]

    def _validate_item(self, value):
        if not isinstance(value, self.subtype):
            raise InvalidData('expected a {}, not {}'.format(
                self.subtype, value))

    def validate(self, value):
        if value is None:
            return
        if not isinstance(value, self.type_):
            raise InvalidData('expected a {}, not {}'.format(
                self.type_, value))
        for item in value:
            self._validate_item(item)
        if self._validate is not None:
            self._validate(value)

    def append(self, value):
        """Append value to option."""
        self._validate_item(value)
        self._value.append(value)

    def count(self, value):
        """Count occurrence of value."""
        return self._value.count(value)

    def index(self, value):
        """Return index of first occurrence of value."""
        return self._value.index(value)

    def extend(self, extension):
        """Extend value of option with extension."""
        self.validate(extension)
        self._value.extend(extension)

    def insert(self, index, value):
        """Insert value at index."""
        self._validate_item(value)
        self._value.insert(index, value)

    def pop(self, index=-1):
        """Remove and return value at index."""
        return self._value.pop(index)

    def remove(self, value):
        """Remove value."""
        self._value.remove(value)

    def reverse(self):
        """Reverse list in place."""
        self._value.reverse()

    def sort(self, key=None, reverse=False):
        """Sort list in place."""
        self._value.sort(key=key, reverse=reverse)

    def __add__(self, other):
        return self._value + other

    def __radd__(self, other):
        return other + self._value

    def __iadd__(self, other):
        self.validate(other)
        self._value += other
        return self

    def __mul__(self, other):
        return self._value * other

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        self._value *= other
        return self

    def __contains__(self, value):
        return value in self._value

    def __iter__(self):
        return iter(self._value)

    def __getitem__(self, index):
        return self._value[index]

    def __setitem__(self, index, value):
        if isinstance(index, int):
            self._validate_item(value)
        else:
            self.validate(value)
        self._value[index] = value

    def __delitem__(self, index):
        del self._value[index]

    def __len__(self):
        return len(self._value)

    def __reversed__(self):
        return reversed(self._value)

class IntegerListOption(StringListOption):

    """List configuration element with integer content."""

    subtype = int

class FloatListOption(StringListOption):

    """List configuration element with float content."""

    subtype = float

class BooleanListOption(StringListOption):

    """List configuration element with boolean content."""

    subtype = bool

class Section(with_metaclass(ConfigMeta, ConfigElement, MappingMixin)):

    """
    Named container that contains ConfigElements.

    Keyword Arguments
    -----------------
    required: bool, optional
        MUST section be present? If no default is provided for any
        required content elements, this can result in a
        MissingData exception. to find out if an optional section
        is complete, see `self.incomplete_count`. Defaults to True
    validate: Callable[Any, None], optional
        additional validation function, defaults to None

    Raises
    ------
    AttributeError:
        if content element is not a `ConfigElement`

    Attributes
    ----------
    creation_counter: int
        global count of config elements, used to maintain field order
    element_name: str
        name of instance, provided by containing class
    type_: type
        python type of variable that this class represents
    action: str
        action for argparse
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
    type_ = dict

    def __init__(
            self,
            required=True,
            validate=None):
        ConfigElement.__init__(
            self,
            doc=self.__doc__,
            required=required,
            validate=validate)

    def has_default(self):
        """Return True because Section always has a default value."""
        return True

    def get_elements(self):
        """Return raw element tree, use with caution."""
        return self._elements

    def get_value(self):
        """Return current content value."""
        result = {}
        for element in self._elements:
            result[element] = self._elements[element].get_value()
        return result

    def set_value(self, value):
        """Validate and store value."""
        raise NotImplementedError

    def construct_parser(self, parser):
        for element in self._elements:
            self._elements[element].construct_parser(parser)

    def extract_data_from_parser(self, command_line_arguments):
        for element in self._elements:
            self._elements[element].extract_data_from_parser(
                command_line_arguments)

    def validate(self, value):
        pass

    def validate_data(self):
        self.incomplete_count = 0
        for element in self._elements:
            try:
                self._elements[element].validate_data()
            except MissingData:
                print(self.required)
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

class InvalidConfigTree(Exception):

    """Inappropriate configuration tree for file type."""

class InvalidData(Exception):

    """User supplied invalid data for a configuration element."""

class MissingData(Exception):

    """An element marked as required is missing a value."""

class Config(with_metaclass(ConfigMeta, MappingMixin)):

    """
    Base class for application configuration.

    Keyword Arguments
    -----------------
    file_name: str, optional
        name of the configuration file, defaults to config
    global_path: pathlib.Path, optional
        overwrite system global configuration path, defaults to None
    user_path: pathlib.Path, optional
        overwrite system user configuration path, defaults to None

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

    def __init__(
            self,
            file_name="config",
            global_path=None,
            user_path=None):
        if self.application is None:
            raise AttributeError(
                'application not set, please provide an application name')
        if self.author is None:
            raise AttributeError(
                'author not set, please provide an application author')
        # validate _elements
        self._validate(self._elements)
        # read global config
        if global_path is None or user_path is None:
            paths = AppDirs(self.application, self.author, self.version)
        if global_path is None:
            global_path = Path(paths.site_config_dir)
        global_path = global_path.joinpath(
            "{}.{}".format(file_name, self._extension))
        if global_path.is_file():
            self._read(global_path, self._elements)
        # read user config
        if user_path is None:
            user_path = Path(paths.user_config_dir)
        user_path = user_path.joinpath(
            "{}.{}".format(file_name, self._extension))
        if user_path.is_file():
            self._read(user_path, self._elements)
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
            self._write(self._elements, self.__doc__)
            sys.exit(True)

        # fetch command line argument data
        for element in self._elements:
            self._elements[element].extract_data_from_parser(
                command_line_arguments)
            # validate _data
            self._elements[element].validate_data()
