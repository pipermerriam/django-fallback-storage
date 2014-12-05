SECRET_KEY = 'arst'

DEFAULT_FILE_STORAGE = 'fallback_storage.storage.FallbackStorage'

FALLBACK_STORAGES = (
    'inmemorystorage.storage.InMemoryStorage',
    'django.core.files.storage.FileSystemStorage',
)
