"""Creates objects utilized for solving crossword puzzles."""
from importlib import reload
import crossword.globs
import crossword.funcs
import crossword.clses


reload(crossword.globs)
reload(crossword.funcs)
reload(crossword.clses)


#Disable pylint flags: wildcard import (I know; I want __all__ variables to be
#available in the package directly), import should be at the top (these are
#being re-imported; ideally, the imports would be at the top, but they need to
#be reloaded first - that way, if crossword is reloaded, so are the submodules)
from crossword.globs import * #pylint: disable=wildcard-import, wrong-import-position
from crossword.funcs import * #pylint: disable=wildcard-import, wrong-import-position
from crossword.clses import * #pylint: disable=wildcard-import, wrong-import-position


__all__ = [*crossword.globs.__all__,
           *crossword.funcs.__all__,
           *crossword.clses.__all__]
