from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-your-secret-key"  # ide majd jöhet saját

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# --- Alap Django alkalmazások + saját appok ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # saját appok
    "users",
    "catalog",
    "billing",
    "compare",
]

# --- Köztes rétegek (Middleware) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # fontos: az auth előtt legyen!
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodcompare.urls"

# --- Template beállítások (adminhoz és saját oldalakhoz is kell) ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # ha van templates mappád a projektben
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

# --- Adatbázis (SQLite) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Felhasználó modell (egyedi) ---
AUTH_USER_MODEL = "users.Felhasznalo"

# --- Nyelv és időzóna ---
LANGUAGE_CODE = "hu-hu"
TIME_ZONE = "Europe/Budapest"
USE_I18N = True
USE_TZ = True

# --- Statikus fájlok ---
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
