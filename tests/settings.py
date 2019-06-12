INSTALLED_APPS = (
    'tracking_model',
    'tests',
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
SECRET_KEY = 'dummy'
