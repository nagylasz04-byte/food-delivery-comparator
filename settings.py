from pathlib import Path

# --- Alapbeállítások ---
BASE_DIR = Path(__file__).resolve().parent
SECRET_KEY = "django-insecure-!foodcompare-demo-secret"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# --- Telepített alkalmazások ---
INSTALLED_APPS = [
    # Django alap appok
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

# --- Middleware rétegek (az adminhoz és bejelentkezéshez is kellenek) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # fontos: auth előtt
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- URL és WSGI beállítások ---
ROOT_URLCONF = "foodcompare.urls"
WSGI_APPLICATION = "foodcompare.wsgi.application"

# --- Adatbázis (SQLite) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Egyedi felhasználómodell ---
AUTH_USER_MODEL = "users.Felhasznalo"

# --- Template beállítások (admin + saját oldalakhoz) ---
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

# --- Statikus fájlok és nyelvi beállítások ---
STATIC_URL = "static/"
LANGUAGE_CODE = "hu-hu"
TIME_ZONE = "Europe/Budapest"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
