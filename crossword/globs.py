"""Create global variables to support crossword solvers"""
from sys import modules


__all__ = ['MIN_LEN']


def export(obj):
    """Adds and object to it's modules __all__"""
    mod = modules[obj.__module__]
    if hasattr(mod, '__all__'):
        mod.__all__.append(obj.__name__)
    else:
        mod.__all__ = [obj.__name__]
    return obj


class _AutoFlag:
    """Autoflag boolean"""
    def __init__(self, default=True):
        """Create an autoflag"""
        self.classes = {}
        self._value = default

    def __bool__(self):
        """Get value from autoflag"""
        return self._value

    def enable(self):
        """Enable the autoflag"""
        self._value = True
        for cls, (method, args, kwargs) in self.classes.items():
            if hasattr(cls, 'instances') and method:
                for obj in cls.instances:
                    if hasattr(obj, method):
                        getattr(obj, method)(*args, **kwargs)

    def disable(self):
        """Disable the autoflag"""
        self._value = False

    def publish(self, cls, *args, **kwargs):
        """Publish a class to be auto-refreshed when the auto flag is toggled"""
        refresh_method = kwargs.pop('refresh_method', None)
        newargs = []
        for arg in args:
            if isinstance(arg, str) and not refresh_method:
                refresh_method = arg
            else:
                newargs.append(arg)
        self.classes[cls] = (refresh_method, newargs, kwargs)

    def unpublish(self, cls):
        """Un-publish a class to be auto-refreshed."""
        self.classes.pop(cls, None)

_AUTO_ON = _AutoFlag()
MIN_LEN = 3


@export
def auto(enabled=True):
    """Enable or disable automatic updates of dependant classes."""
    prev = bool(_AUTO_ON)
    if enabled and not _AUTO_ON:
        _AUTO_ON.enable()
    if _AUTO_ON and not enabled:
        _AUTO_ON.disable()
    return (prev, enabled)
