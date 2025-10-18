from pathlib import Path

# --- Alapok ---
BASE_DIR = Path(__file__).resolve().parent.parent  # .../foodcompare/ -> projekt gyökér
SECRET_KEY = "django-insecure-replace-me-for-production"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# --- Telepített alkalmazások ---
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Saját appok
    "users",
    "catalog",
    "billing",
    "compare",
]

# Egyedi user modell (ahogy korábban létrehoztuk)
AUTH_USER_MODEL = "users.Felhasznalo"

# --- Middleware (sorrend fontos) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # auth előtt legyen
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodcompare.urls"

# --- Templating (admin + saját sablonok) ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # a projekt gyökérben lévő "templates" mappa:
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

WSGI_APPLICATION = "foodcompare.wsgi.application"

# --- Adatbázis (SQLite fejlesztéshez) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Bejelentkezés/átirányítások ---
# Frontend login/logout settings
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# --- Lokálizáció ---
LANGUAGE_CODE = "hu-hu"
TIME_ZONE = "Europe/Budapest"
USE_I18N = True
USE_TZ = True

# --- Statikus fájlok ---
STATIC_URL = "static/"
# opcionális: ha van saját /static mappád a projekt gyökérben
STATICFILES_DIRS = [BASE_DIR / "static"]

# --- Egyebek ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
