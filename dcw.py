from contextlib import suppress as _suppress
from functools import wraps as _wraps
from gc import collect as _collect
from importlib import reload as _reload
from sys import modules as _modules

if __name__ != '__main__':
    #If name != main, then this is being imported
    #Don't need to worry about backing up the crossword variable, because
    #we can't overwrite global crossword, only module level
    try:
        _crossword
    except NameError:
        import crossword as _crossword
    else:
        _reload(_crossword)
else:
    if 'crossword' in _modules:
        _crossword = _modules['crossword']
        #If Checker is defined but isn't the standard from crossword, the user
        #has mucked with it.  Reload crossword to ensure everything is good
        with _suppress(NameError):
            if Checker is not _crossword.Checker:
                _reload(_crossword)
    else:
        import crossword as _crossword
from crossword import *

class Checker(Checker):
    @_wraps(Checker.__init__)
    def __init__(self, wordfile='words.txt', *args, **kwargs):
        super().__init__(*args, wordfile=wordfile, **kwargs)
Checker._instances = Checker.__bases__[0]._instances

class Solver(Solver):
    @_wraps(Solver.__init__)
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], Checker.__bases__[0]):
            super().__init__(*args, **kwargs)
        elif isinstance(kwargs.get('checker'), Checker.__bases__[0]):
            super().__init__(*args, **kwargs)
        elif Checker.instances:
            super().__init__(Checker.instances[0], *args, **kwargs)
        else:
            super().__init__(Checker(), *args, **kwargs)
Solver._instances = Solver.__bases__[0]._instances

_collect()
