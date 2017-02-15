"""Usage example for user_config."""
from user_config import Config, Section, StringOption, IntegerOption

class MyConfig(Config):

    """This will be displayed in the configuration documentation."""

    application = "my_application"
    author = "me"

    class GeneralSection(Section):
        """General information."""
        name = StringOption(
            doc="your name",
            default="unknown person")
        age = IntegerOption(
            doc="your age",
            required=True)
    general = GeneralSection()
    class AddressSection(Section):
        """shipping address"""
        street = StringOption(
            doc="street including house number",
            required=True)
        city = StringOption(required=True)
    address = AddressSection(required=False)

if __name__ == "__main__":
    CONFIG = MyConfig()
    print("hello there, {}!".format(CONFIG.general.name))
