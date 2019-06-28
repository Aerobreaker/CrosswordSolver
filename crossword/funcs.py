"""Create package-level functions and classes for use in crossword solvers."""
from functools import wraps, WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES


from crossword.globs import export


__all__ = []


@export
def auto(enabled=True):
    """Enable or disable automatic updates of dependant classes."""
    #Disable pylint flags: Cyclic import (I know, but it's necessary; that's why
    #the import is inside the function - so that when the function gets called,
    #this module is already imported and there won't be problems)
    from crossword.clses import _AUTO_ON #pylint: disable=cyclic-import
    prev = bool(_AUTO_ON)
    if enabled and not prev:
        _AUTO_ON.enable()
    if prev and not enabled:
        _AUTO_ON.disable()
    return prev, enabled


def nodoc_wraps(wrapped,
                assigned=tuple(set(WRAPPER_ASSIGNMENTS)-{'__doc__'}),
                updated=WRAPPER_UPDATES):
    """Like functools.wraps but without updating __doc__.  See wraps for more"""
    return wraps(wrapped, assigned, updated)


@export
def group_count(iterable):
    """Groups an iterable by values and counts the lengths of the groups."""
    #Groupby splits it into groups.  But the items consists of each individual
    #element in the group.  So convert to a list and read the length of said
    #list
    from itertools import groupby
    for grp, items in groupby(iterable):
        yield grp, len(list(items))
#


@export
def get_words(words):
    """Splits out a parameter set into individual words.

    First, it splits the input parameters by space.  Then, it chains them
    together.  Then, it joins them together delimited by , and splits them
    out once again.  The end result is that words can be provided as
    individual parameters, or a single comma separated string or a single
    space separated string or some combination thereof.

    Args:
        words: The word list to split out
    Returns:
        A set (hash set) of words which were in the provided input
    """
    from itertools import chain
    #Split on spaces, then chain the resulting arrays together
    #Join into a single string delimited by comma
    words = ','.join(chain.from_iterable(i.split() for i in words))
    #Split out the joined string by comma (to also split any single words which
    #contained a comma).  Ignore empty strings.
    return set(i for i in words.split(',') if i)


class InstanceTrackerProperties(type):
    """Create a metaclass which has an instances property"""
    @wraps(type.__init__)
    def __init__(cls, *args, **kwargs):
        """Instantiate a class"""
        from weakref import WeakValueDictionary
        super().__init__(*args, **kwargs)
        cls._instances = WeakValueDictionary()

    @property
    def instances(cls):
        """Return the instances of a class"""
        return list(cls._instances.values())


#Disable pylint flags: too few public methods (this is only here as a template
#for other classes to inherit from; public methods are unnecessary)
@export
class InstanceTracker(metaclass=InstanceTrackerProperties): #pylint: disable=too-few-public-methods
    """Creates a class which tracks it's instances"""
    #Disable pylint flags: unused argument (yeah, I don't need them here but I
    #have to take them so they can be passed to __init__)
    def __new__(cls, *args, **kwargs): #pylint: disable=unused-argument
        """Create a new object and log the object in the instances"""
        new = super().__new__(cls)
        cls._instances[id(new)] = new
        return new
