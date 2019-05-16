"""Create package-level functions and classes for use in crossword solvers."""
from enum import auto as _auto, Enum
from functools import wraps
from gc import collect


from crossword.globs import export


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


class BaseClassProperties(type):
    """Create a metaclass which has an instances property"""
    @wraps(type.__init__)
    def __init__(cls, *args, **kwargs):
        """Instantiate a class"""
        from weakref import WeakSet
        super().__init__(*args, **kwargs)
        cls._instances = WeakSet()

    @property
    def instances(cls):
        """Return the instances of a class"""
        return list(cls._instances)


@export
class BaseClass(metaclass=BaseClassProperties):
    """Creates a class which tracks it's instances"""
    def __init__(self):
        """Create a weak reference to self for instance tracking"""
        type(self)._instances.add(self)

    def get_instances(self):
        """Return instances of the object's class"""
        return type(self).instances

    @classmethod
    def collect(cls):
        """Collect garbage"""
        if cls.instances:
            collect()


@export
class Direction(Enum):
    """Enumerator to indicate right or down direction."""
    RIGHT = _auto()
    DOWN = _auto()
