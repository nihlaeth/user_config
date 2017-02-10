"""User config management."""
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
        '_user_extension',
        '_global_extension',
        '_reader',
        '_writer',
        '_validator']
    new_attributes = {'_elements': {}}
    for attribute in cls_attributes:
        if isinstance(cls_attributes[attribute], ConfigElement):
            new_attributes['_elements'] = cls_attributes[attribute]
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
            new_attributes['_user_extension'] = extension['user_extension']
            new_attributes['_global_extension'] = extension['global_extension']
            new_attributes['_reader'] = extension['reader']
            new_attributes['_writer'] = extension['writer']
            new_attributes['_validator'] = extension['validator']
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

    Parameters
    ----------
    command_line_arguments: TODO
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

    def __init__(self, command_line_arguments):
        if self.application is None:
            raise AttributeError(
                'application not set, please provide an application name')
        # TODO: validate _elements
        # TODO: populate _data with defaults
        # TODO: get configuration paths
        # TODO: read global config
        # TODO: read user config
        # TODO: construct a commandline parser
        # TODO: put command line argument data into _data
        # TODO: validate _data
