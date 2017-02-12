"""Test ConfigElement and subclasses."""
import argparse
import pytest

from user_config import ConfigElement, InvalidData

def validate_length(value):
    """Custom validator."""
    if len(value) > 3:
        raise InvalidData('we cant handle more than three characters')

# pylint:disable=no-self-use
class TestConfigElement(object):

    def test_init(self):
        with pytest.raises(InvalidData):
            config_element = ConfigElement(default=42)
        config_element = ConfigElement(doc="test")
        assert config_element.doc == "test"
        assert config_element.required
        config_element = ConfigElement(required=False)
        assert not config_element.required
        config_element = ConfigElement(short_name='f')
        # pylint: disable=protected-access
        assert config_element._short_name == '-f'
        config_element = ConfigElement(short_name='-f')
        assert config_element._short_name == '-f'
        config_element = ConfigElement(long_name='force')
        assert config_element._long_name == '--force'
        config_element = ConfigElement(long_name='--force')
        assert config_element._long_name == '--force'
        config_element = ConfigElement(
            default='hi', validate=validate_length)
        assert config_element.get_default() == 'hi'
        with pytest.raises(InvalidData):
            config_element = ConfigElement(
                default='high', validate=validate_length)

    def test_default(self):
        config_element = ConfigElement()
        assert not config_element.has_default()
        assert config_element.get_default() is None
        config_element = ConfigElement(default="test")
        assert config_element.has_default()
        assert config_element.get_default() == "test"

    def test_parser(self):
        config_element = ConfigElement()
        config_element.element_name = "test"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        arguments = vars(parser.parse_args(['--test', 'success']))
        assert arguments['test'] == 'success'
        data = {}
        config_element.extract_data_from_parser(arguments, data)
        assert data['test'] == 'success'
