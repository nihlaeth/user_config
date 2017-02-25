"""Test ConfigElement and subclasses."""
import argparse
import pytest

from user_config import (
    ConfigElement,
    MissingData,
    InvalidData,
    StringListOption,
    IntegerListOption,
    FloatListOption,
    BooleanListOption,
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

class TestStringListOption(object):

    def test_init(self):
        list_option = StringListOption()
        list_option = StringListOption(additive=True)
        assert list_option._additive is True

    def test_set_value(self):
        list_option = StringListOption()
        assert list_option.get_value() is None
        with pytest.raises(InvalidData):
            list_option.set_value(5)
        list_option.set_value([])
        assert len(list_option.get_value()) == 0
        list_option.set_value(["test"])
        assert len(list_option.get_value()) == 1
        with pytest.raises(InvalidData):
            list_option.set_value([5])

        list_option = StringListOption(additive=True)
        list_option.set_value([])
        assert len(list_option.get_value()) == 0
        list_option.set_value(["test"])
        assert len(list_option.get_value()) == 1
        list_option.set_value(["test"])
        assert len(list_option.get_value()) == 1
        list_option.set_value(["something_else"])
        assert len(list_option.get_value()) == 2

    def test_extract_data_from_parser(self):
        list_option = StringListOption()
        list_option.element_name = "list_option"
        parser = argparse.ArgumentParser(prog="test application")
        list_option.construct_parser(parser)

        # one argument
        arguments = vars(parser.parse_args(['--list_option', '5']))
        list_option.extract_data_from_parser(arguments)
        list_option.validate_data()
        assert len(list_option.get_value()) == 1

        # two arguments
        arguments = vars(parser.parse_args([
            '--list_option', '5', '--list_option', 'test']))
        list_option.extract_data_from_parser(arguments)
        list_option.validate_data()
        assert len(list_option.get_value()) == 2

        # test list addition
        list_option = StringListOption(additive=True)
        list_option.element_name = "list_option"

        # one argument
        arguments = vars(parser.parse_args(['--list_option', '5']))
        list_option.extract_data_from_parser(arguments)
        list_option.validate_data()
        assert len(list_option.get_value()) == 1

        # one argument
        arguments = vars(parser.parse_args(['--list_option', '6']))
        list_option.extract_data_from_parser(arguments)
        list_option.validate_data()
        assert len(list_option.get_value()) == 2

        # two arguments
        arguments = vars(parser.parse_args([
            '--list_option', '5', '--list_option', 'test']))
        list_option.extract_data_from_parser(arguments)
        list_option.validate_data()
        assert len(list_option.get_value()) == 3

    def test_list_methods(self):
        list_option = StringListOption(default=[])
        with pytest.raises(InvalidData):
            list_option.append(0)
        list_option.append("0")
        assert len(list_option.get_value()) == 1
        assert list_option.count("0") == 1
        assert list_option.index("0") == 0
        with pytest.raises(InvalidData):
            list_option.extend([1])
        list_option.extend(["1"])
        assert len(list_option.get_value()) == 2
        with pytest.raises(InvalidData):
            list_option.insert(2, 2)
        list_option.insert(2, "2")
        assert len(list_option.get_value()) == 3
        assert list_option.pop() == "2"
        assert len(list_option.get_value()) == 2
        list_option.remove("1")
        assert len(list_option.get_value()) == 1
        list_option += ["1"]
        assert len(list_option.get_value()) == 2
        list_option.reverse()
        assert list_option[0] == "1"
        list_option.sort()
        assert list_option[0] == "0"
        assert (list_option + ["2"])[2] == "2"
        assert (["-1"] + list_option)[0] == "-1"
        assert (list_option * 2)[3] == "1"
        assert len(2 * list_option) == 4
        list_option *= 2
        assert len(list_option.get_value()) == 4
        assert "1" in list_option
        assert "2" not in list_option
        count = 0
        for _ in list_option:
            count += 1
        assert count == 4
        assert next(reversed(list_option)) == "1"
        del list_option[0]
        assert len(list_option.get_value()) == 3

# pylint: disable=unsubscriptable-object
class TestIntegerListOption(object):

    def test_init(self):
        list_option = IntegerListOption()
        with pytest.raises(InvalidData):
            list_option.set_value(["5"])
        list_option.set_value([5])
        assert list_option.get_value()[0] == 5

class TestFloatListOption(object):

    def test_init(self):
        list_option = FloatListOption()
        with pytest.raises(InvalidData):
            list_option.set_value([5])
        list_option.set_value([5.])
        assert list_option.get_value()[0] == 5.

class TestBooleanListOption(object):

    def test_init(self):
        list_option = BooleanListOption()
        with pytest.raises(InvalidData):
            list_option.set_value([1])
        list_option.set_value([True])
        assert list_option.get_value()[0] is True

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
