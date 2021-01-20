from os import environ

SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=0, fixed_payment=5)

SESSION_CONFIGS = [
    dict(
        name="Control",
        num_demo_participants=1,
        app_sequence=["main"],
        treatment=0,
    ),
    dict(
        name="BTS",
        num_demo_participants=2,
        app_sequence=["main"],
        treatment=1,
        additional_payment=50,
    ),

]

LANGUAGE_CODE = "sk"
REAL_WORLD_CURRENCY_CODE = "CZK"
USE_POINTS = False
DEMO_PAGE_INTRO_HTML = ""
ROOMS = [dict(
    name="stefunko", display_name="Stefunko")]

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

SECRET_KEY = "blahblah"

# if an app is included in SESSION_CONFIGS, you don"t need to list it here
INSTALLED_APPS = ["otree"]
