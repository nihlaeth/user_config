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

# pylint: disable=missing-docstring
class EmptySection(Section):

    pass

def test_validate():
    # valid trees
    ini_validate(None, OrderedDict())
    ini_validate(None, OrderedDict([
        ('section_a', Section()),
        ('section_b', Section())]))

    class SectionA(Section):
        element_a = StringOption()
    class SectionB(Section):
        element_b = IntegerOption()
        element_c = BooleanOption()
        element_d = FloatOption()
    ini_validate(None, OrderedDict([
        ('section_a', SectionA()),
        ('section_b', SectionB())]))
    # invalid trees
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, "nonsense")
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, {})
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, [EmptySection()])
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, OrderedDict(something_else=5))
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, OrderedDict(not_a_section=StringOption()))
    class NestedSection(Section):
        another_section = EmptySection()
    with pytest.raises(InvalidConfigTree):
        ini_validate(None, OrderedDict(
            nested_section=NestedSection()))

def test_read():
    config_directory = Path(__file__).parents[0] / 'test_read'
    class SectionOne(Section):
        string = StringOption()
        multiline_string = StringOption()
        integer = IntegerOption()
        float = FloatOption()
        boolean = BooleanOption()
    class SectionTwo(Section):
        empty_string = StringOption()
        empty_integer = IntegerOption()
        empty_float = FloatOption()
        empty_boolean = BooleanOption()
        missing_key = StringOption()
    config_tree = OrderedDict([
        ('section_one', SectionOne()),
        ('section_two', SectionTwo()),
        ('missing_section', EmptySection())])
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
    class InvalidIntegerSection(Section):
        not_an_integer = IntegerOption()
    config_tree = OrderedDict(section_three=InvalidIntegerSection())
    with pytest.raises(ValueError):
        ini_read(
            None, config_directory / 'data_types.cfg', config_tree, None)
    class InvalidFloatSection(Section):
        not_a_float = FloatOption()
    config_tree = OrderedDict(section_three=InvalidFloatSection())
    with pytest.raises(ValueError):
        ini_read(
            None, config_directory / 'data_types.cfg', config_tree, None)
    class InvalidBooleanSection(Section):
        not_a_boolean = BooleanOption()
    config_tree = OrderedDict(section_three=InvalidBooleanSection())
    with pytest.raises(ValueError):
        ini_read(
            None, config_directory / 'data_types.cfg', config_tree, None)

def test_register_extension():
    result = register_extension()
    assert result['extension'] == 'cfg'
    assert result['read'] is ini_read
    assert result['write'] is ini_write
    assert result['validate'] is ini_validate

# pylint: disable=no-self-use,function-redefined
class TestWrite(object):

    def test_class_docstring(self, capsys):
        empty_elements = OrderedDict()
        one_section = OrderedDict(section=EmptySection())
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
        empty_section = OrderedDict(section=EmptySection())
        ini_write(None, empty_section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n\n"
        assert err == ""

        # section with docstring
        class DocumentedSection(Section):
            """test"""
        section = OrderedDict(section=DocumentedSection())
        ini_write(None, section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n## test\n\n\n"
        assert err == ""

        # optional section
        optional_section = OrderedDict(
            section=EmptySection(required=False))
        ini_write(None, optional_section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n## OPTIONAL_SECTION\n\n\n"
        assert err == ""

        # optional section with docstring
        section = OrderedDict(
            section=DocumentedSection(required=False))
        ini_write(None, section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n## test\n## OPTIONAL_SECTION\n\n\n"
        assert err == ""

        # multiple sections
        section = OrderedDict()
        section['first_section'] = EmptySection()
        section['section'] = DocumentedSection()
        section['last_section'] = EmptySection()
        ini_write(None, section, None, None)
        out, err = capsys.readouterr()
        assert out == "[first_section]\n\n[section]\n## test\n\n\n[last_section]\n\n"
        assert err == ""

        # optional section with content
        class SectionWithContent(Section):
            string = StringOption(default="value")
        optional_section = OrderedDict(section=SectionWithContent(
            required=False))
        optional_section['section'].get_default()
        ini_write(None, optional_section, None, None)
        out, err = capsys.readouterr()
        assert out == "[section]\n## OPTIONAL_SECTION\n\n# string = value\n\n\n"
        assert err == ""

    def test_item_default(self, capsys):
        # required item with default value
        class MySection(Section):
            string = StringOption(default="value", required=True)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(default="value", required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(required=True)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(default="value", required=True)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(default="value", required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(required=True)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(
                doc="test", default="value", required=True)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(
                doc="test", default="value", required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(doc="test", required=True)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(doc="test", required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(default="value", required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(default="a\nb\nc", required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            integer = IntegerOption(default=7, required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            float = FloatOption(default=2., required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            boolean = BooleanOption(default=True, required=False)
        elements = OrderedDict(section=MySection())
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
        class MySection(Section):
            string = StringOption(default="value", required=False)
            item_two = StringOption(doc="option two", default="2")
        elements = OrderedDict(section=MySection())
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
