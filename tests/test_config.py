"""Test Config."""
import sys
from pathlib import Path
import pytest
from user_config import Config, Section, StringOption

class FallbackConfig(Config):

    """Test configuration fallback."""

    application = "test"
    author = "nobody"

    class GeneralSection(Section):

        """General section."""

        string = StringOption(default="default")

    general = GeneralSection()

def test_default():
    config_directory = Path(__file__).parents[0] / 'test_config'
    sys.argv = [sys.argv[0]]
    config = FallbackConfig(
        file_name="default",
        global_path=config_directory / 'global',
        user_path=config_directory / 'user')
    assert config.general.string == "default"

def test_global():
    config_directory = Path(__file__).parents[0] / 'test_config'
    sys.argv = [sys.argv[0]]
    config = FallbackConfig(
        file_name="global",
        global_path=config_directory / 'global',
        user_path=config_directory / 'user')
    assert config.general.string == "global"

def test_user():
    config_directory = Path(__file__).parents[0] / 'test_config'
    sys.argv = [sys.argv[0]]
    config = FallbackConfig(
        file_name="user",
        global_path=config_directory / 'global',
        user_path=config_directory / 'user')
    assert config.general.string == "user"

def test_cli():
    config_directory = Path(__file__).parents[0] / 'test_config'
    sys.argv = [sys.argv[0], '--string', 'cli']
    config = FallbackConfig(
        file_name="user",
        global_path=config_directory / 'global',
        user_path=config_directory / 'user')
    assert config.general.string == "cli"

def test_no_cli():
    config_directory = Path(__file__).parents[0] / 'test_config'
    sys.argv = [sys.argv[0], 'invalid_argument']
    config = FallbackConfig(
        file_name="user",
        global_path=config_directory / 'global',
        user_path=config_directory / 'user',
        cli=False)
    assert config.general.string == "user"

def test_required_attributes():
    class NoApplication(Config):
        """Test missing application attribute."""
        author = "nobody"
    with pytest.raises(AttributeError):
        NoApplication()
    class NoAuthor(Config):
        """Test missing author attribute."""
        application = "test"
    with pytest.raises(AttributeError):
        NoAuthor()
