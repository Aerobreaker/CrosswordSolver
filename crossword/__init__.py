"""Creates objects utilized for solving crossword puzzles."""
from importlib import reload
from sys import modules
import crossword.globs
import crossword.funcs
import crossword.clses


__all__ = []
for mod in ('crossword.clses', 'crossword.funcs', 'crossword.globs'):
    reload(modules[mod])
    __all__.extend(modules[mod].__all__)
    var = ''
    for var in modules[mod].__all__:
        globals()[var] = getattr(modules[mod], var)


del mod, var
