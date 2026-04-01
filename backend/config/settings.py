import os
import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_csv_env(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


DEFAULT_CATEGORY_NAMES = [
    "Electronics",
    "Clothing",
    "Home",
    "Books",
    "Beauty",
    "Sports",
]

DEBUG = _get_bool_env("DJANGO_DEBUG", _get_bool_env("DEBUG", False))
RUNNING_TESTS = "test" in sys.argv

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG or RUNNING_TESTS:
        SECRET_KEY = "change-me-django-dev"
    else:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY environment variable is required")

ALLOWED_HOSTS = _get_csv_env("DJANGO_ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    if DEBUG or RUNNING_TESTS:
        ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
    else:
        raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS environment variable is required")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "common",
    "accounts",
    "catalog",
    "orders",
]

MEDIA_STORAGE_BACKEND = os.getenv("DJANGO_MEDIA_STORAGE_BACKEND", "filesystem").strip().lower()
MEDIA_PUBLIC_BASE_URL = os.getenv("DJANGO_MEDIA_PUBLIC_BASE_URL", "").strip()

if MEDIA_STORAGE_BACKEND == "s3":
    INSTALLED_APPS.append("storages")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}
if not DEBUG and DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured("Production DATABASE_URL must use PostgreSQL")

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

if MEDIA_STORAGE_BACKEND == "s3":
    aws_bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME", "").strip()
    if not aws_bucket_name:
        raise ImproperlyConfigured(
            "AWS_STORAGE_BUCKET_NAME is required when DJANGO_MEDIA_STORAGE_BACKEND=s3"
        )

    aws_custom_domain = os.getenv("AWS_S3_CUSTOM_DOMAIN", "").strip() or None
    aws_location = os.getenv("AWS_LOCATION", "").strip().strip("/")
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": os.getenv("AWS_ACCESS_KEY_ID", "").strip() or None,
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", "").strip() or None,
            "bucket_name": aws_bucket_name,
            "region_name": os.getenv("AWS_S3_REGION_NAME", "").strip() or None,
            "endpoint_url": os.getenv("AWS_S3_ENDPOINT_URL", "").strip() or None,
            "custom_domain": aws_custom_domain,
            "default_acl": None,
            "file_overwrite": False,
            "querystring_auth": _get_bool_env("AWS_QUERYSTRING_AUTH", False),
        },
    }
    if aws_location:
        STORAGES["default"]["OPTIONS"]["location"] = aws_location
    if not MEDIA_PUBLIC_BASE_URL and aws_custom_domain:
        MEDIA_PUBLIC_BASE_URL = f"https://{aws_custom_domain}"
else:
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": MEDIA_ROOT,
            "base_url": MEDIA_URL,
        },
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = _get_csv_env("DJANGO_CORS_ALLOWED_ORIGINS")
if (DEBUG or RUNNING_TESTS) and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

CSRF_TRUSTED_ORIGINS = _get_csv_env("DJANGO_CSRF_TRUSTED_ORIGINS")
if (DEBUG or RUNNING_TESTS) and not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = list(CORS_ALLOWED_ORIGINS)

CORS_ALLOW_CREDENTIALS = True

MANUAL_PAYMENT_BANK_NAME = os.getenv("MANUAL_PAYMENT_BANK_NAME", "").strip()
MANUAL_PAYMENT_ACCOUNT_NAME = os.getenv("MANUAL_PAYMENT_ACCOUNT_NAME", "").strip()
MANUAL_PAYMENT_ACCOUNT_NUMBER = os.getenv(
    "MANUAL_PAYMENT_ACCOUNT_NUMBER",
    "",
).strip()
MANUAL_PAYMENT_NOTE = os.getenv("MANUAL_PAYMENT_NOTE", "").strip()

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = _get_bool_env("DJANGO_SECURE_SSL_REDIRECT", False)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "EXCEPTION_HANDLER": "common.exceptions.api_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("DJANGO_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    ),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
