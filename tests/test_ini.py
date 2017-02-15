"""Test ini backend."""
from collections import OrderedDict
from pathlib import Path
import pytest

from user_config import (
    Section,
    StringOption,
    BooleanOption,
    IntegerOption,
    FloatOption,
    InvalidConfigTree)
from user_config.ini import ini_validate, ini_read, ini_write, register_extension

def test_validate():
    # valid trees
    ini_validate(None, OrderedDict())
    ini_validate(None, OrderedDict(
        section_a=Section(),
        section_b=Section()))
    ini_validate(None, OrderedDict(
        section_a=Section(element_a=StringOption()),
        section_b=Section(
            element_b=IntegerOption(),
            element_c=BooleanOption(),
            element_d=FloatOption())))
    # invalid trees
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, "nonsense")
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, {})
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, [Section()])
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, OrderedDict(something_else=5))
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, OrderedDict(not_a_section=StringOption()))
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, OrderedDict(
            nested_section=Section(another_section=Section())))

def test_read():
    config_directory = Path(__file__).parents[0] / 'test_read'
    config_tree = OrderedDict(
        section_one=Section(
            string=StringOption(),
            multiline_string=StringOption(),
            integer=IntegerOption(),
            float=FloatOption(),
            boolean=BooleanOption()),
        section_two=Section(
            empty_string=StringOption(),
            empty_integer=IntegerOption(),
            empty_float=FloatOption(),
            empty_boolean=BooleanOption(),
            missing_key=StringOption()),
        missing_section=Section())
    data = OrderedDict()
    for section in config_tree:
        data[section] = config_tree[section].get_default()
    ini_read(None, config_directory / 'data_types.cfg', config_tree, None)
    assert data['section_one'].string == "some text"
    assert ' '.join([
        word.strip() for word in data[
            'section_one'].multiline_string.split('\n')]) == "some lines of text"
    assert data['section_one'].integer == 5
    assert data['section_one'].float == 2.3
    assert data['section_one'].boolean is True
    assert data['section_two'].empty_string is None
    assert data['section_two'].empty_integer is None
    assert data['section_two'].empty_float is None
    assert data['section_two'].empty_boolean is None
    assert data['section_two'].missing_key is None

    # test invalid values
    config_tree = OrderedDict(section_three=Section(
        not_an_integer=IntegerOption()))
    with pytest.raises(ValueError):
        ini_read(
            None, config_directory / 'data_types.cfg', config_tree, None)
    config_tree = OrderedDict(section_three=Section(
        not_a_float=FloatOption()))
    with pytest.raises(ValueError):
        ini_read(
            None, config_directory / 'data_types.cfg', config_tree, None)
    config_tree = OrderedDict(section_three=Section(
        not_a_boolean=BooleanOption()))
    with pytest.raises(ValueError):
        ini_read(
            None, config_directory / 'data_types.cfg', config_tree, None)

def test_register_extension():
    result = register_extension()
    assert result['extension'] == 'cfg'
    assert result['read'] is ini_read
    assert result['write'] is ini_write
    assert result['validate'] is ini_validate

# pylint: disable=no-self-use
class TestWrite(object):

    def test_class_docstring(self, capsys):
        empty_elements = OrderedDict()
        one_section = OrderedDict(section=Section())
        doc = "test"

        # empty
        ini_write(None, empty_elements, None, None)
        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""

        # only docstring
        ini_write(None, empty_elements, None, doc)
        out, err = capsys.readouterr()
        assert out == "## test\n\n"
        assert err == ""

        # only section
        ini_write(None, one_section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n\n"
        assert err == ""

        # docstring and section
        ini_write(None, one_section, None, doc)
        out, err = capsys.readouterr()
        assert out == "## test\n\n[section]\n\n"
        assert err == ""

    def test_section(self, capsys):
        # empty section
        empty_section = OrderedDict(section=Section())
        ini_write(None, empty_section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n\n"
        assert err == ""

        # section with docstring
        section = OrderedDict(section=Section(doc="test"))
        ini_write(None, section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n## test\n\n\n"
        assert err == ""

        # optional section
        optional_section = OrderedDict(section=Section(required=False))
        ini_write(None, optional_section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n## OPTIONAL_SECTION\n\n\n"
        assert err == ""

        # optional section with docstring
        section = OrderedDict(
            section=Section(doc="test", required=False))
        ini_write(None, section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n## test\n## OPTIONAL_SECTION\n\n\n"
        assert err == ""

        # multiple sections
        section = OrderedDict(
            first_section=Section(),
            section=Section(doc="test"),
            last_section=Section())
        ini_write(None, section, None, None)
        out, err = capsys.readouterr()
        assert out == "[first_section]\n\n[section]\n## test\n\n\n[last_section]\n\n"
        assert err == ""

        # optional section with content
        optional_section = OrderedDict(section=Section(
            string=StringOption(default="value"), required=False))
        optional_section['section'].get_default()
        ini_write(None, optional_section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n## OPTIONAL_SECTION\n\n# string = value\n\n\n"
        assert err == ""

    def test_item_default(self, capsys):
        # required item with default value
        elements = OrderedDict(section=Section(
            string=StringOption(default="value", required=True)))
        elements['section'].get_default()
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# string = value",
            "",
            "",
            ""])
        assert err == ""

        # optional item with default value
        elements = OrderedDict(section=Section(
            string=StringOption(default="value", required=False)))
        elements['section'].get_default()
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# string = value",
            "",
            "",
            ""])
        assert err == ""

        # required item without default value
        elements = OrderedDict(section=Section(
            string=StringOption(required=True)))
        elements['section'].get_default()
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "## REQUIRED",
            "# string = ",
            "string = ",
            "",
            "",
            ""])
        assert err == ""

        # optional item without default value
        elements = OrderedDict(section=Section(
            string=StringOption(required=False)))
        elements['section'].get_default()
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# string = ",
            "",
            "",
            ""])
        assert err == ""

    def test_item_overwriting(self, capsys):
        # required item with default value, overwritten
        elements = OrderedDict(section=Section(
            string=StringOption(default="value", required=True)))
        elements['section'].get_default()
        elements['section'].string = "overwritten"
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# string = value",
            "string = overwritten",
            "",
            "",
            ""])
        assert err == ""

        # optional item with default value, overwritten
        elements = OrderedDict(section=Section(
            string=StringOption(default="value", required=False)))
        elements['section'].get_default()
        elements['section'].string = "overwritten"
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# string = value",
            "string = overwritten",
            "",
            "",
            ""])
        assert err == ""

        # required item without default value, overwritten
        elements = OrderedDict(section=Section(
            string=StringOption(required=True)))
        elements['section'].get_default()
        elements['section'].string = "overwritten"
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "## REQUIRED",
            "# string = ",
            "string = overwritten",
            "",
            "",
            ""])
        assert err == ""

        # optional item without default value, overwritten
        elements = OrderedDict(section=Section(
            string=StringOption(required=False)))
        elements['section'].get_default()
        elements['section'].string = "overwritten"
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# string = ",
            "string = overwritten",
            "",
            "",
            ""])
        assert err == ""

    def test_item_docstring(self, capsys):
        # required item with default value, with docstring
        elements = OrderedDict(section=Section(
            string=StringOption(
                doc="test", default="value", required=True)))
        elements['section'].get_default()
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "## test",
            "# string = value",
            "",
            "",
            ""])
        assert err == ""

        # optional item with default value, with docstring
        elements = OrderedDict(section=Section(
            string=StringOption(
                doc="test", default="value", required=False)))
        elements['section'].get_default()
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "## test",
            "# string = value",
            "",
            "",
            ""])
        assert err == ""

        # required item without default value, with docstring
        elements = OrderedDict(section=Section(
            string=StringOption(doc="test", required=True)))
        elements['section'].get_default()
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "## test",
            "## REQUIRED",
            "# string = ",
            "string = ",
            "",
            "",
            ""])
        assert err == ""

        # optional item without default value, with docstring
        elements = OrderedDict(section=Section(
            string=StringOption(doc="test", required=False)))
        elements['section'].get_default()
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "## test",
            "# string = ",
            "",
            "",
            ""])
        assert err == ""

    def test_item_data_types(self, capsys):
        # string, with default
        elements = OrderedDict(section=Section(
            string=StringOption(default="value", required=False)))
        elements['section'].get_default()
        elements['section'].string = "overwritten"
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# string = value",
            "string = overwritten",
            "",
            "",
            ""])
        assert err == ""

        # multiline string, with default
        elements = OrderedDict(section=Section(
            string=StringOption(default="a\nb\nc", required=False)))
        elements['section'].get_default()
        elements['section'].string = "d\ne\nf"
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# string = a",
            "#     b",
            "#     c",
            "string = d",
            "    e",
            "    f",
            "",
            "",
            ""])
        assert err == ""

        # integer, with default
        elements = OrderedDict(section=Section(
            integer=IntegerOption(default=7, required=False)))
        elements['section'].get_default()
        elements['section'].integer = 8
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# integer = 7",
            "integer = 8",
            "",
            "",
            ""])
        assert err == ""

        # float, with default
        elements = OrderedDict(section=Section(
            float=FloatOption(default=2., required=False)))
        elements['section'].get_default()
        elements['section'].float = 3.5
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# float = 2.0",
            "float = 3.5",
            "",
            "",
            ""])
        assert err == ""

        # boolean, with default
        elements = OrderedDict(section=Section(
            boolean=BooleanOption(default=True, required=False)))
        elements['section'].get_default()
        elements['section'].boolean = False
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# boolean = True",
            "boolean = False",
            "",
            "",
            ""])
        assert err == ""

    def test_sequential_items(self, capsys):
        elements = OrderedDict(section=Section(
            string=StringOption(default="value", required=False),
            item_two=StringOption(doc="option two", default="2")))
        elements['section'].get_default()
        elements['section'].string = "overwritten"
        ini_write(None, elements, None, None)
        out, err = capsys.readouterr()
        assert out == '\n'.join([
            "[section]",
            "# string = value",
            "string = overwritten",
            "",
            "## option two",
            "# item_two = 2",
            "",
            "",
            ""])
        assert err == ""
