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

# pylint:disable=no-self-use,protected-access
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

    def test_value(self):
        no_default = ConfigElement()
        assert no_default.get_value() is None
        no_default.set_value("valid")
        assert no_default.get_value() == "valid"
        with pytest.raises(InvalidData):
            no_default.set_value(-5)

        with_default = ConfigElement(default="default")
        assert with_default.get_value() == "default"
        with_default.set_value("valid")
        assert with_default.get_value() == "valid"
        with pytest.raises(InvalidData):
            with_default.set_value(-5)

    def test_parser(self, capsys):
        # test normal usage
        config_element = ConfigElement()
        config_element.element_name = "test"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        arguments = vars(parser.parse_args(['--test', 'success']))
        assert arguments['test'] == 'success'
        config_element.extract_data_from_parser(arguments)
        assert config_element.get_value() == 'success'

        # test absent option
        config_element = ConfigElement()
        config_element.element_name = "test"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        arguments = vars(parser.parse_args([]))
        assert arguments['test'] is None
        config_element.extract_data_from_parser(arguments)
        assert config_element.get_value() is None

        # test alternate name
        config_element = ConfigElement(long_name="--testing")
        config_element.element_name = "test"
        parser = argparse.ArgumentParser(prog="test application")
        config_element.construct_parser(parser)
        arguments = vars(parser.parse_args(['--test', 'success']))
        assert arguments['testing'] == 'success'
        config_element.extract_data_from_parser(arguments)
        assert config_element.get_value() == 'success'

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
        config_element._value = 5
        with pytest.raises(InvalidData):
            config_element.validate_data()
        config_element.validate("ok")

        config_element = ConfigElement(validate=validate_length)
        config_element.element_name = 'test'
        with pytest.raises(InvalidData):
            config_element.validate("some words")
        config_element._value = "some words"
        with pytest.raises(InvalidData):
            config_element.validate_data()
        with pytest.raises(InvalidData):
            config_element.validate(5)
        config_element._value = 5
        with pytest.raises(InvalidData):
            config_element.validate_data()
        config_element.validate("ok")
        config_element.set_value("ok")
        config_element.validate_data()

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
        config_element.extract_data_from_parser(arguments)
        assert config_element.get_value() == 5

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
        config_element.extract_data_from_parser(arguments)
        assert config_element.get_value() == 5.3

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
        config_element.extract_data_from_parser(arguments)
        assert config_element.get_value() is True

# pylint: disable=missing-docstring,function-redefined,attribute-defined-outside-init
class EmptySection(Section):

    pass

class TestSection(object):

    def test_init(self):
        empty_section = EmptySection()
        assert empty_section.has_default()
        assert empty_section.get_default() is None
        assert len(empty_section) == 0

        class MySection(Section):
            name = StringOption(default="test")
        section = MySection()

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
        class MySection(Section):
            one = IntegerOption()
            two = IntegerOption(required=False)
        optional_section = MySection(required=False)
        optional_section.element_name = "section"
        parser = argparse.ArgumentParser(prog="test application")
        optional_section.construct_parser(parser)

        # missing required value
        arguments = vars(parser.parse_args([]))
        optional_section.extract_data_from_parser(arguments)
        optional_section.validate_data()
        assert optional_section.incomplete_count == 1

        # missing required value, optional value provided
        arguments = vars(parser.parse_args(['--two', '42']))
        optional_section.extract_data_from_parser(arguments)
        optional_section.validate_data()
        assert optional_section.incomplete_count == 1

        # required value provided
        arguments = vars(parser.parse_args(['--one', '5']))
        optional_section.extract_data_from_parser(arguments)
        optional_section.validate_data()
        assert optional_section.incomplete_count == 0

        # test required section
        # refresh element instances, since their values are shared across
        # section instances
        class MySection(Section):
            one = IntegerOption()
            two = IntegerOption(required=False)
        required_section = MySection(required=True)
        required_section.element_name = "section"

        # missing required value
        arguments = vars(parser.parse_args([]))
        required_section.extract_data_from_parser(arguments)
        with pytest.raises(MissingData):
            required_section.validate_data()
        assert required_section.incomplete_count == 0

        # missing required value, optional value provided
        arguments = vars(parser.parse_args(['--two', '42']))
        required_section.extract_data_from_parser(arguments)
        with pytest.raises(MissingData):
            required_section.validate_data()
        assert required_section.incomplete_count == 0

        # required value provided
        arguments = vars(parser.parse_args(['--one', '5']))
        required_section.extract_data_from_parser(arguments)
        required_section.validate_data()
        assert required_section.incomplete_count == 0
