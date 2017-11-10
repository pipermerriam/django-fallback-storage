from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import (
    Storage,
    get_storage_class,
)


def concatenate_exceptions(exceptions):
    return '\n'.join((
        "{0}: {1}".format(b, e) for e, b in exceptions.items()
    ))


def fallback_method(method_name):
    """
    Returns a method that will return the first successful response from a
    storage backend.
    """
    def method(self, *args, **kwargs):
        exceptions = {}

        for backend_class, backend_method in self.get_backend_methods(method_name):
            try:
                return backend_method(*args, **kwargs)
            except Exception as e:
                exceptions[backend_class] = e
                continue

        if exceptions:
            if len(exceptions) == 1:
                raise exceptions[0]
            raise Exception(concatenate_exceptions(exceptions))
        else:
            raise AttributeError(
                "No backend has the method `{0}`".format(method_name),
            )
    method.__name__ = method_name
    return method


class FallbackStorage(Storage):
    def __init__(self, backends=None):
        if backends is None:
            try:
                assert settings.FALLBACK_STORAGES
                backends = settings.FALLBACK_STORAGES
            except (AttributeError, AssertionError):
                raise ImproperlyConfigured("The setting `FALLBACK_STORAGES` is "
                                           "either missing or empty")
        self.backend_classes = backends

    def get_backends(self):
        for backend_class in self.backend_classes:
            backend = get_storage_class(backend_class)()
            yield backend_class, backend

    def get_backend_methods(self, method_name):
        for backend_class, backend in self.get_backends():
            if hasattr(backend, method_name):
                yield backend_class, getattr(backend, method_name)

    # Primary Methods
    _open = fallback_method('_open')
    _save = fallback_method('_save')

    # Optional Methods
    delete = fallback_method('delete')
    size = fallback_method('size')
    accessed_time = fallback_method('accessed_time')
    created_time = fallback_method('created_time')
    modified_time = fallback_method('modified_time')

    # Public API Methods
    get_valid_name = fallback_method('get_valid_name')
    path = fallback_method('path')

    def get_available_name(self, name, **kwargs):
        available_name = None

        while not available_name:
            potential_names = set()
            exceptions = {}

            for backend_class, backend_method in self.get_backend_methods('get_available_name'):
                # First we add each potential name from the storage backends to the
                # potential_names set.
                try:
                    potential_names.add(backend_method(name, **kwargs))
                except Exception as e:
                    exceptions[backend_class] = e
                    continue

            # If we have more than 1 potential name we know that one of the storage backends
            # in use has a file with the specified name 'name'. As such, we're going to remove
            # the current 'name' value from the set, and assign the next potential name to the
            # variable 'name' before running the loop again with the new potential name.
            if len(potential_names) > 1:
                potential_names.remove(name)
                name = next(iter(potential_names))
                continue

            if len(potential_names) == 1:
                available_name = next(iter(potential_names))
            elif exceptions:
                if len(exceptions) == 1:
                    raise exceptions[0]
                raise Exception(concatenate_exceptions(exceptions))
            else:
                raise AttributeError("No backend found with the method `get_available_name`")

        return available_name

    def exists(self, *args, **kwargs):
        exceptions = {}
        return_values = []

        for backend_class, backend_method in self.get_backend_methods('exists'):
            try:
                return_values.append(backend_method(*args, **kwargs))
            except Exception as e:
                exceptions[backend_class] = e
                continue

        if return_values:
            return any(return_values)
        elif exceptions:
            if len(exceptions) == 1:
                raise exceptions[0]
            raise Exception(concatenate_exceptions(exceptions))
        else:
            raise AttributeError("No backend found with the method `exists`")

    def listdir(self, *args, **kwargs):
        exceptions = {}
        directories = []
        files = []

        for backend_class, backend_method in self.get_backend_methods('listdir'):
            try:
                dirs, files_ = backend_method(*args, **kwargs)
                directories.extend(dirs)
                files.extend(files_)
            except Exception as e:
                exceptions[backend_class] = e
                continue

        if (any(directories) or any(files)) or not exceptions:
            return directories, files
        elif exceptions:
            if len(exceptions) == 1:
                raise exceptions[0]
            raise Exception(concatenate_exceptions(exceptions))
        else:
            raise AttributeError("No backend found with the method `listdir`")

    def url(self, name):
        exceptions = {}

        for backend_class, backend in self.get_backends():
            if not hasattr(backend, 'url') or not hasattr(backend, 'exists'):
                continue

            if not backend.exists(name):
                continue
            try:
                return backend.url(name)
            except Exception as e:
                exceptions[backend_class] = e
                continue
        if exceptions:
            if len(exceptions) == 1:
                raise exceptions[0]
            raise Exception(concatenate_exceptions(exceptions))
        else:
            last_backend = get_storage_class(self.backend_classes[-1])()
            try:
                return last_backend.url(name)
            except AttributeError:
                raise AttributeError("No backend found with the method `url`")
