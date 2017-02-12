"""Test ConfigElement and subclasses."""
import argparse
import pytest

from user_config import (
    ConfigElement,
    MissingData,
    InvalidData,
    Section,
    StringOption,
    IntegerOption,
    FloatOption,
    BooleanOption)


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

class TestStringOption(object):

    """
    At this time, StringOption is equivalent to ConfigElement.
    """

class TestIntegerOption(object):

    def test_init(self):
        with pytest.raises(InvalidData):
            config_element = IntegerOption(default="5")
        config_element = IntegerOption(default=5)
        assert config_element.get_default() == 5

    def test_parser(self, capsys):
        config_element = IntegerOption(doc="helpful text")
        config_element.element_name = "number"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        arguments = vars(parser.parse_args(['--number', '5']))
        assert arguments['number'] == 5
        data = {}
        config_element.extract_data_from_parser(arguments, data)
        assert data['number'] == 5

        parser.print_help()
        out, err = capsys.readouterr()
        assert out == """usage: test application [-h] [--number NUMBER]

optional arguments:
  -h, --help       show this help message and exit
  --number NUMBER  helpful text
"""
        assert err == ""

class TestFloatOption(object):

    def test_init(self):
        with pytest.raises(InvalidData):
            config_element = FloatOption(default="5")
        with pytest.raises(InvalidData):
            config_element = FloatOption(default=5)
        config_element = FloatOption(default=5.2)
        assert config_element.get_default() == 5.2

    def test_parser(self):
        config_element = FloatOption(doc="helpful text")
        config_element.element_name = "number"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        arguments = vars(parser.parse_args(['--number', '5.3']))
        assert arguments['number'] == 5.3
        data = {}
        config_element.extract_data_from_parser(arguments, data)
        assert data['number'] == 5.3

class TestBooleanOption(object):

    def test_init(self):
        with pytest.raises(InvalidData):
            config_element = BooleanOption(default="true")
        with pytest.raises(InvalidData):
            config_element = BooleanOption(default=0)
        config_element = BooleanOption(default=True)
        assert config_element.get_default() is True

    def test_parser(self):
        config_element = BooleanOption(doc="helpful text")
        config_element.element_name = "all_good"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        arguments = vars(parser.parse_args(['--all_good', 'yes']))
        assert arguments['all_good'] is True
        data = {}
        config_element.extract_data_from_parser(arguments, data)
        assert data['all_good'] is True

class TestSection(object):

    def test_init(self):
        section = Section(default=42)
        assert section.get_default() is section
        section = Section(default=None)
        assert section.has_default()
        assert len(section) == 0
        with pytest.raises(AttributeError):
            section = Section(keyword="not a config element")
        section = Section(name=StringOption(default="test"))
        section.get_default()

        # test map methods
        assert len(section) == 1
        assert section.name == "test"
        assert section['name'] == "test"
        section.name = "something else"
        assert section.name == "something else"
        with pytest.raises(InvalidData):
            # pylint: disable=redefined-variable-type
            section.name = False
        section.not_field = None
        assert section.not_field is None
        with pytest.raises(AttributeError):
            section['not_field'] = None
        for field in section:
            assert field == "name"
            iterated = True
        assert iterated
        assert "name" in section
        assert section.get("nonexisting", "I'm fine") == "I'm fine"
        # TODO: test update, keys, values and items

    def test_incomplete_count(self):
        # test optional section
        section = Section(
            required=False,
            one=IntegerOption(),
            two=IntegerOption(required=False))
        section.get_default()
        section.element_name = "section"
        parser = argparse.ArgumentParser(prog="test application")
        section.construct_parser(parser)

        # missing required value
        arguments = vars(parser.parse_args([]))
        section.extract_data_from_parser(arguments, None)
        section.validate_data(None)
        assert section.incomplete_count == 1

        # missing required value, optional value provided
        arguments = vars(parser.parse_args(['--two', '42']))
        section.extract_data_from_parser(arguments, None)
        section.validate_data(None)
        assert section.incomplete_count == 1

        # required value provided
        arguments = vars(parser.parse_args(['--one', '5']))
        section.extract_data_from_parser(arguments, None)
        section.validate_data(None)
        assert section.incomplete_count == 0

        # test required section
        section = Section(
            required=True,
            one=IntegerOption(),
            two=IntegerOption(required=False))
        section.get_default()
        section.element_name = "section"
        parser = argparse.ArgumentParser(prog="test application")
        section.construct_parser(parser)

        # missing required value
        arguments = vars(parser.parse_args([]))
        section.extract_data_from_parser(arguments, None)
        with pytest.raises(MissingData):
            section.validate_data(None)
        assert section.incomplete_count == 0

        # missing required value, optional value provided
        arguments = vars(parser.parse_args(['--two', '42']))
        section.extract_data_from_parser(arguments, None)
        with pytest.raises(MissingData):
            section.validate_data(None)
        assert section.incomplete_count == 0

        # required value provided
        arguments = vars(parser.parse_args(['--one', '5']))
        section.extract_data_from_parser(arguments, None)
        section.validate_data(None)
        assert section.incomplete_count == 0
