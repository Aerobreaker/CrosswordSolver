from contextlib import suppress as _suppress
from functools import wraps as _wraps
from gc import collect as _collect
from importlib import reload as _reload
from sys import modules as _modules

if __name__ != '__main__':
    #If name != main, then this is being imported
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
                _reload(_modules['crossword.clses'])
                _reload(_modules['crossword.funcs'])
                _reload(_modules['crossword.globs'])
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
        from numbers import Real
        #If first argument is a checker, use that
        #If first argument isn't a checker, but checker is a kwarg, use that
        #If neither, use first checker instance or a new instance
        self.letters = self.layout = self.checker = self._lengths = 'holding'
        checker = kwargs.get('checker')
        letters = kwargs.get('letters', '')
        layout = kwargs.get('layout', None)
        if 'lengths' in kwargs:
            minlen, maxlen = kwargs['lengths']
        else:
            minlen = kwargs.pop('minlen', None)
            maxlen = kwargs.pop('maxlen', None)
        newargs = []
        newkwargs = {}
        for arg in args:
            if not checker and isinstance(arg, Checker.__bases__[0]):
                checker = arg
            elif not letters and isinstance(arg, str):
                letters = arg
            elif not layout and isinstance(arg, Layout):
                layout = arg
            elif (not minlen and
                  isinstance(arg, tuple) and
                  len(arg) == 2 and 
                  isinstance(arg[0], Real) and
                  isinstance(arg[1], Real)):
                minlen, maxlen = arg
            elif not minlen and isinstance(arg, Real):
                minlen = arg
            elif not maxlen and isinstance(arg, Real):
                maxlen = arg
            else:
                newargs.append(arg)
        if not checker:
            if Checker.instances:
                checker = Checker.instances[0]
            else:
                checker = Checker()
        if not minlen:
            minlen = 3
        if not maxlen:
            maxlen = inf
        newkwargs = {**kwargs,
                     'checker':checker,
                     'letters':letters,
                     'layout':layout,
                     'lengths':(minlen, maxlen)}
        super().__init__(*newargs, **newkwargs)
Solver._instances = Solver.__bases__[0]._instances

def show(l, m=3):
    Solver(l, minlen=m).print()

_collect()
