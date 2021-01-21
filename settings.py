from os import environ
import os


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
    name="stefunko",
    display_name="Stefunko",

)]

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable


SECRET_KEY = "blahblah"

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# STATICFILES_DIRS = os.path.join(BASE_DIR, "/main/static/")
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
# if an app is included in SESSION_CONFIGS, you don"t need to list it here
INSTALLED_APPS = ["otree"]
# environ["DATABASE_URL"] = "postgres://postgres@localhost/django_db"
# environ["REDIS_URL"] = "redis://localhost:6379"
# # environ["OTREE_AUTH_LEVEL"] = "DEMO"
# environ["OTREE_ADMIN_PASSWORD"] = "odraSe5ku"
# environ["OTREE_PRODUCTION"] = "0"
# ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")
PRODUCTION = 0

# if environ.get("OTREE_PRODUCTION") not in {None, "", "0"}:
#     DEBUG = False
# else:
#     DEBUG = True
