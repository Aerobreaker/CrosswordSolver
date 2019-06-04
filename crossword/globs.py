"""Create global variables to support crossword solvers"""
__all__ = ['MIN_LEN']


def export(obj):
    """Adds and object to it's modules __all__"""
    from sys import modules
    mod = modules[obj.__module__]
    if hasattr(mod, '__all__'):
        mod.__all__.append(obj.__name__)
    else:
        mod.__all__ = [obj.__name__]
    return obj


MIN_LEN = 3
