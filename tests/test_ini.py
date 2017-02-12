"""Test ini backend."""
from collections import OrderedDict
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
