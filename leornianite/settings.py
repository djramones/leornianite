"""Django settings for the leornianite project."""

from email.utils import parseaddr
from pathlib import Path

import environ


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("LEOR_SECRET_KEY")
DEBUG = env.bool("LEOR_DEBUG")
ALLOWED_HOSTS = env.list("LEOR_ALLOWED_HOSTS")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env("LEOR_DB_HOST"),
        "PORT": env("LEOR_DB_PORT"),
        "NAME": env("LEOR_DB_NAME"),
        "USER": env("LEOR_DB_USER"),
        "PASSWORD": env("LEOR_DB_PASSWORD"),
    }
}


# Application definition

INSTALLED_APPS = [
    "notes.apps.NotesConfig",
    "formtools",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.staticfiles",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "leornianite.urls"
WSGI_APPLICATION = "leornianite.wsgi.application"

if DEBUG:
    # Debug Toolbar
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]

# Models

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Security

SECURE_SSL_REDIRECT = env.bool("LEOR_SECURE_SSL_REDIRECT")
SESSION_COOKIE_SECURE = env.bool("LEOR_SESSION_COOKIE_SECURE")
CSRF_COOKIE_SECURE = env.bool("LEOR_CSRF_COOKIE_SECURE")


# Templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# Authentication

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files

STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "static-collected"
STATIC_URL = "static/"


# Email

DEFAULT_FROM_EMAIL = env("LEOR_DEFAULT_FROM_EMAIL")
SERVER_EMAIL = env("LEOR_SERVER_EMAIL")
ADMINS = list(parseaddr(email) for email in env("LEOR_ADMINS").split(","))
EMAIL_SUBJECT_PREFIX = "[Leornianite] "
if env.bool("LEOR_EMAIL_LOCAL_DEV"):
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
