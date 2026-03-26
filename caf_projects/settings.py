"""
Django settings for caf_projects project.

- Base de dados: SQLite local por defeito; em produção use DATABASE_URL (Supabase PostgreSQL).
- Ficheiros: pasta media/ local por defeito; com variáveis SUPABASE_S3_* use Supabase Storage (API S3).
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-d!ez-@g+1in=a(c#61eim)p3xjfp_wmj1zrwp2e3m$h*eh9eq9",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "caf.serveousercontent.com",
    "caf.serveusercontent.com",
    "caf-projects.onrender.com",
]
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])
for _h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(","):
    _h = _h.strip()
    if _h and _h not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_h)

CSRF_TRUSTED_ORIGINS = [
    "https://caf.serveousercontent.com",
    "https://caf.serveusercontent.com",
    "https://caf-projects.onrender.com",
]
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    CSRF_TRUSTED_ORIGINS.append(
        f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}"
    )
for _o in os.environ.get("CSRF_TRUSTED_ORIGINS_EXTRA", "").split(","):
    _o = _o.strip()
    if _o and _o not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_o)

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "submissions",
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

ROOT_URLCONF = "caf_projects.urls"

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

WSGI_APPLICATION = "caf_projects.wsgi.application"


# Database — SQLite se DATABASE_URL não estiver definido
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Password validation
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


LANGUAGE_CODE = "pt-pt"

TIME_ZONE = "Europe/Lisbon"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

# --- Media: Supabase Storage (S3) ou disco local ---
MEDIA_URL = "/media/"

_supabase_storage_ready = all(
    os.environ.get(k)
    for k in (
        "SUPABASE_S3_ACCESS_KEY_ID",
        "SUPABASE_S3_SECRET_ACCESS_KEY",
        "SUPABASE_STORAGE_BUCKET",
        "SUPABASE_S3_ENDPOINT",
        "SUPABASE_S3_REGION",
    )
)

if _supabase_storage_ready:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": os.environ["SUPABASE_STORAGE_BUCKET"],
                "access_key": os.environ["SUPABASE_S3_ACCESS_KEY_ID"],
                "secret_key": os.environ["SUPABASE_S3_SECRET_ACCESS_KEY"],
                "endpoint_url": os.environ["SUPABASE_S3_ENDPOINT"],
                "region_name": os.environ["SUPABASE_S3_REGION"],
                "addressing_style": "path",
                "default_acl": None,
                "querystring_auth": True,
                "file_overwrite": False,
                "querystring_expire": 3600,
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    MEDIA_ROOT = None
else:
    _media_dir = BASE_DIR / "media"
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {
                "location": str(_media_dir),
                "base_url": MEDIA_URL,
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    MEDIA_ROOT = _media_dir

# Autenticação — Área do professor (apenas utilizadores staff)
LOGIN_URL = "/professor/entrar/"
LOGIN_REDIRECT_URL = "/professor/"
LOGOUT_REDIRECT_URL = "/"
