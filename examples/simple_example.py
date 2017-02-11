"""Usage example for user_config."""
from user_config import Config, Section, StringOption, IntegerOption

class MyConfig(Config):

    """This will be displayed in the configuration documentation."""

    application = "my_application"
    author = "me"
    general = Section(
        name=StringOption(
            doc="your name",
            default="unknown person"),
        age=IntegerOption(
            doc="your age",
            required=True))
    address = Section(
        street=StringOption(
            doc="street including house number",
            required=True),
        city=StringOption(required=True),
        required=False,
        doc="shipping address")

if __name__ == "__main__":
    CONFIG = MyConfig()
    print("hello there, {}!".format(CONFIG.general.name))
