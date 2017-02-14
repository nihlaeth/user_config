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
