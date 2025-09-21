from .base import *

# --- Development Settings ---
DEBUG = True

# For development, we can use a more permissive secret key
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-+2_m$k60shf26&ycl!6twzu(wk9!fsdqo=*+x64$6=sobkd#hy")

# Allow all hosts in development
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "*"]

# Development database - can use SQLite for quick setup or PostgreSQL as configured
# Uncomment below to use SQLite for development:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Keep PostgreSQL from base.py for consistency with your current setup
