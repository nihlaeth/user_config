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

    def test_parser(self, capsys):
        # test normal usage
        config_element = ConfigElement()
        config_element.element_name = "test"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        arguments = vars(parser.parse_args(['--test', 'success']))
        assert arguments['test'] == 'success'
        data = {}
        config_element.extract_data_from_parser(arguments, data)
        assert data['test'] == 'success'

        # test absent option
        config_element = ConfigElement()
        config_element.element_name = "test"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        arguments = vars(parser.parse_args([]))
        assert arguments['test'] is None
        data = {}
        config_element.extract_data_from_parser(arguments, data)
        assert 'test' not in data

        # test alternate name
        config_element = ConfigElement(long_name="--testing")
        config_element.element_name = "test"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        arguments = vars(parser.parse_args(['--test', 'success']))
        assert arguments['testing'] == 'success'
        data = {}
        config_element.extract_data_from_parser(arguments, data)
        assert data['test'] == 'success'

        # test help text
        config_element = ConfigElement(doc="helpful text")
        config_element.element_name = "test"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        parser.print_help()
        out, err = capsys.readouterr()
        assert out == """usage: test application [-h] [--test TEST]

optional arguments:
  -h, --help   show this help message and exit
  --test TEST  helpful text
"""
        assert err == ""

        # test help text
        config_element = ConfigElement(
            doc="helpful text", short_name="t", long_name="test_me")
        config_element.element_name = "test"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        parser.print_help()
        out, err = capsys.readouterr()
        assert out == """usage: test application [-h] [-t TEST_ME]

optional arguments:
  -h, --help            show this help message and exit
  -t TEST_ME, --test_me TEST_ME
                        helpful text
"""
        assert err == ""

    def test_validate(self):
        config_element = ConfigElement()
        config_element.element_name = 'test'
        with pytest.raises(InvalidData):
            config_element.validate(5)
        with pytest.raises(InvalidData):
            config_element.validate_data({'test': 5})
        config_element.validate("ok")

        config_element = ConfigElement(validate=validate_length)
        config_element.element_name = 'test'
        with pytest.raises(InvalidData):
            config_element.validate("some words")
        with pytest.raises(InvalidData):
            config_element.validate_data({'test': "some words"})
        with pytest.raises(InvalidData):
            config_element.validate(5)
        with pytest.raises(InvalidData):
            config_element.validate_data({'test': 5})
        config_element.validate("ok")
        config_element.validate_data({'test': "ok"})
