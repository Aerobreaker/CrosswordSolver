"""Create classes for use in crossword solvers."""
from math import inf
from weakref import WeakKeyDictionary


from crossword.globs import Direction, MIN_LEN, export
from crossword.funcs import group_count, get_words, InstanceTracker, wraps


__all__ = ['inf']


class _AutoFlag:
    """Autoflag boolean"""
    def __init__(self, default=True):
        """Create an autoflag"""
        self.classes = {}
        self._value = default

    def __bool__(self):
        """Get value from autoflag"""
        return self._value

    def enable(self, silent=False):
        """Enable the autoflag"""
        self._value = True
        if not silent:
            self.refresh(lambda obj: True)

    def disable(self):
        """Disable the autoflag"""
        self._value = False

    #Disable pylint flags: kwarg before varargs (this is fine, why is this even
    #a pylint error?)
    def publish(self, cls, refresh_method='', *args, **kwargs): #pylint: disable=keyword-arg-before-vararg
        """Publish a class to be auto-refreshed when the auto flag is toggled"""
        pass

    #Disable pylint flags: inconsistent return statements (I know - when used as
    #a wrapper, it needs to return a function; when called with a class arg,
    #there's no need to return anything), method already defined (yeah, exactly;
    #I want this functionality with the original signature), missing-docstring
    #(um, it wraps another function, it gets the docstring from there, duh?)
    #Idea: Perhaps just return the wrapper function in all cases?  It can still
    #be called directly with:
    #_AutoFlag().publish(refresh_method, *args, **kwargs)(cls)
    @wraps(publish)
    def publish(self, *args, **kwargs): #pylint: disable=inconsistent-return-statements, function-redefined, missing-docstring
        refresh_method = kwargs.pop('refresh_method', '')
        cls = kwargs.pop('cls', None)
        newargs = []
        for arg in args:
            if isinstance(arg, type) and not cls:
                cls = arg
            elif isinstance(arg, str) and not refresh_method:
                refresh_method = arg
            else:
                newargs.append(arg)
        if cls:
            if hasattr(cls, 'instances'):
                self.classes[cls] = (refresh_method, newargs, kwargs)
            return
        def pub(cls):
            if hasattr(cls, 'instances'):
                self.classes[cls] = (refresh_method, newargs, kwargs)
            return cls
        return pub

    def unpublish(self, cls):
        """Un-publish a class to be auto-refreshed."""
        self.classes.pop(cls, None)

    def refresh(self, tester):
        """Refreshes all published classes"""
        from gc import collect
        collect()
        for cls, (method, args, kwargs) in self.classes.items():
            for obj in cls.instances:
                if tester(obj) and hasattr(obj, method):
                    getattr(obj, method)(*args, **kwargs)

    def auto_class(self, *auto_methods, test_method='', nauto_methods=()):
        """Decorator to automatically refresh after specified methods"""
        auto_self = self
        def wrapper(method, test_method='', no_refresh=False):
            @wraps(method)
            def wrapped(self, *args, **kwargs):
                refresh = bool(auto_self)
                auto_self.disable()
                tester = getattr(self, test_method, lambda obj: True)
                outp = method(self, *args, **kwargs)
                if refresh:
                    auto_self.enable(silent=True)
                    if not no_refresh:
                        auto_self.refresh(tester)
                return outp
            return wrapped
        def auto(cls):
            for method in auto_methods:
                meth = getattr(cls, method, None)
                if meth and hasattr(cls, test_method):
                    setattr(cls, method, wrapper(meth, test_method))
            for method in nauto_methods:
                meth = getattr(cls, method, None)
                if meth:
                    setattr(cls, method, wrapper(meth, no_refresh=True))
            return cls
        return auto


_AUTO_ON = _AutoFlag()
_CHECKER_SIGNATURES = WeakKeyDictionary()


_ = ('set_word', 'rem_word', 'set_letter', 'rem_letter', 'clear')
@_AUTO_ON.auto_class(*_, test_method='_test')
@export
class Slot(InstanceTracker):
    """Creates a slot to track an opening to put a word into.

    This object is created as a helper to the Layout object.  It tracks
    location, length, and direction of a word slot.  Notably, it's possible to
    have two words which wholly overlap as long as they're different lengths.

    Attributes:
        attributes: The size, position, and direction of the Slot
        has_word: Boolean indicating whether or not the Slot has a word assigned
        overlaps: Dictionary of overlapping slots
        word: The word which has been inserted into the Slot
    """
    def __init__(self, size, position=(0, 0), direction=Direction.RIGHT):
        """Initializes a Slot object to track an open slot for a word.

        Args:
            size: The length of the word slot
            position: Optional.  Tuple indicating the (row, column) on which the
                      Slot starts.  Defaults to (0, 0).
            direction: Optional.  The directionality of the Slot.  Defaults to
                       Direction.RIGHT
        """
        self.attributes = (size, position, direction)
        self.overlaps = {}
        self.word = self._word = [''] * size
        self._empty = size
        self.has_word = False

    def __repr__(self):
        """Returns an internal representation of a Slot object."""
        size, position, direction = self.attributes
        return 'Slot(size={}, position={}, direction={})'.format(size,
                                                                 position,
                                                                 direction)

    #__hash__ and __eq__ are used to identify an object.  Two objects are
    #considered duplicates if the hashes are the same and they compare equal to
    #one another.

    def __hash__(self):
        """Returns a hash for the Slot object."""
        return hash(self.attributes)

    def __eq__(self, other):
        """Returns true if equal to other."""
        return self.attributes == other

    def __len__(self):
        """Returns the length of the Slot."""
        return self.attributes[0]

    def __getitem__(self, key):
        """Indexes into the word contained in the Slot."""
        return self.word[key]

    def _test(self, solver):
        if not getattr(solver, 'layout', None):
            return False
        return self in getattr(solver.layout, 'all_slots', set())

    def check_word(self, word):
        """Checks to see if the specified word will fit in the Slot.

        Checks the overlaps with this slot to ensure that inserting the target
        word will not cause letter conflicts.

        Args:
            word: The word to check.
        Returns:
            Boolean indicating whether the word will cause conflicts
        """
        if len(word) != len(self) or self.has_word:
            return False
        #Overlap dictionary has the slots as keys and the index of the overlap
        #as values.  Slot1.overlaps[Slot2] == index in Slot1 at which the
        #overlap occurs.
        for other, other_ind in self.overlaps.items():
            ind = other.overlaps[self]
            #If other has a letter in the overlap and it doesn't match the
            #letter which will be overlapping, the word won't fit
            if other[other_ind] and other[other_ind] != word[ind]:
                return False
        for cur, new in zip(self.word, word):
            if cur and cur != new:
                return False
        return True

    def set_word(self, word):
        """Stores the specified word into the Slot.

        Stores the specified word into this Slot, without checking overlaps.
        To ensure there are no overlap conflicts, use check_word first.

        Args:
            word: The word to insert into the Slot
        Raises:
            AttributeError: Length of specified word does not match length
                of the Slot
            TypeError: The Slot already contains a word
        """
        if len(word) != len(self):
            raise AttributeError('target word is incorrect length')
        if self.has_word:
            raise TypeError('slot word is already set')
        self.word = word
        self.has_word = True

    def rem_word(self):
        """Removes the stored word from the Slot, preserving any set letters."""
        self.has_word = False
        self.word = self._word

    def set_letter(self, ind, let):
        """Inserts a letter into the specified index.

        Args:
            ind: The index in this Slot in which to insert the letter
            let: The letter to insert
        Raises:
            AttributeError: The target index already contains a different letter
        """
        if self.word[ind] and self.word[ind] != let:
            raise AttributeError('target letter is already set')
        if self.word[ind] == let:
            return
        self.word[ind] = self._word[ind] = let
        self._empty -= 1
        if self._empty == 0:
            self.has_word = True
            self.word = ''.join(self.word)

    def rem_letter(self, ind):
        """Removes any set letters from the specified index

        Args:
            ind: The index in this Slot from which to remove the letter
        """
        if self.has_word:
            self.word = list(self.word)
            self.has_word = False
        if self.word[ind]:
            self._empty += 1
        self.word[ind] = self._word[ind] = ''

    def add_overlap(self, ind, other, other_ind):
        """Adds an overlap with the specified Slot.

        Args:
            ind: The index in this Slot where the overlap occurs
            other: The Slot which this Slot overlaps with
            other_ind: The index in other where the overlap occurs
        """
        self.overlaps[other] = other_ind
        other.overlaps[self] = ind

    def clear(self):
        """Removes the word and all letters from the Slot."""
        self.word = self._word = [''] * len(self)
        self._empty = len(self)
        self.has_word = False


_ = ('clear', 'set_letter', 'rem_letter', 'set_extra', 'rem_extra', 'set_word',
     'rem_word')
@_AUTO_ON.auto_class(*_, test_method='_test', nauto_methods=('solve',))
@export
class Layout(InstanceTracker):
    """Creates a Layout object to find and track slots in the provided board.

    Attributes:
        layout: Grid which mimics the original, but with pointers to the
                appropriate slots and indicies from which to draw letters
        slots: Dictionary of Slots indexed by length
    """
    def __init__(self, layout):
        """Initializes a Layout object with the provided layout.

        Args:
            layout: The grid (list of lists) to parse into a Layout
        """
        from itertools import chain
        def clean_edges(matrix):
            from collections import deque
            matrix = deque(matrix)
            while not any(matrix[0]):
                matrix.popleft()
            while not any(matrix[-1]):
                matrix.pop()
            return matrix
        self._layout = layout
        #In order to transpose properly, push all of the rows out to match the
        #longest row
        length = max(len(row) for row in layout)
        for row_ind, row in enumerate(layout):
            if len(row) < length:
                layout[row_ind] = tuple(row) + (0,) * (length-len(row))
        #Remove empty rows from the top and bottom
        layout = clean_edges(layout)
        #Transpose, then remove empty columns from left and right
        layout = clean_edges(zip(*layout))
        #Transpose back
        layout = list(zip(*layout))
        self._layout = tuple(layout)
        self.slots = {}
        self.extras = set()
        layout = [[[(None, 0)] * 2 for _ in range(length)] for _ in layout]
        #Iterate through the rows groupwise, creating and logging Slots with a
        #right directionality
        for row_ind, row in enumerate(self._layout):
            col_ind = 0
            for val, count in group_count(row):
                if val and count >= MIN_LEN:
                    slot = Slot(count, position=(row_ind, col_ind))
                    self.slots.setdefault(count, []).append(slot)
                    for i in range(count):
                        layout[row_ind][col_ind+i][0] = (slot, i)
                col_ind += count
        #Iterate through the columns groupwise, creating and logging Slots with
        #a down directionality
        for col_ind, col in enumerate(zip(*self._layout)):
            row_ind = 0
            for val, count in group_count(col):
                if val and count >= MIN_LEN:
                    slot = Slot(count,
                                position=(row_ind, col_ind),
                                direction=Direction.DOWN)
                    self.slots.setdefault(count, []).append(slot)
                    for i in range(count):
                        overlap = layout[row_ind+i][col_ind][0]
                        if overlap[0]:
                            slot.add_overlap(i, *overlap)
                        layout[row_ind+i][col_ind][1] = (slot, i)
                row_ind += count
        #Save off the dict of slots and the layout of slots
        self.layout = layout
        self.all_slots = set(chain.from_iterable(self.slots.values()))

    def __repr__(self):
        """Returns an internal represntation of the Layout."""
        return 'Layout(layout={})'.format(self._layout)

    def __len__(self):
        """Returns the number of rows in the Layout."""
        return len(self.layout)

    def __getitem__(self, key):
        """Gets the slots at the specified position.

        Args:
            key: The key to get
        Raises:
            IndexError: row or column is outside the bounds of the layout
        """
        if isinstance(key, tuple) and len(key) == 2:
            row, col = key
            if abs(row) > len(self.layout):
                raise IndexError('row index out of range')
            if abs(col) > len(self.layout[row]):
                raise IndexError('column index out of range')
            if row < 0:
                row = len(self.layout) + row
            if col < 0:
                col = len(self.layout[row]) + col
            rgt, lft = self.layout[row][col]
            rgt = rgt[0]
            lft = lft[0]
            if rgt and lft:
                return rgt, lft
            if rgt:
                return (rgt,)
            if lft:
                return (lft,)
            return ()
        return [self[key, i] for i in range(len(self.layout[key]))]

    def __iter__(self):
        """Iterate through the Layout"""
        return self.layout.__iter__()

    def _test(self, solver):
        return self is getattr(solver, 'layout', None)

    def clear(self):
        """Removes all words and letters from a Layout."""
        for slot in self.all_slots:
            slot.clear()
        self.extras.clear()

    def set_letter(self, letter, row, column):
        """Sets a letter in a specific position to constrain solutions.

        Notably, when using this method, if any slots at the specified position
        contain a word with a conflicting letter, the word will be removed.

        Args:
            letter: The letter to insert
            row: The row at which to insert
            column: The column at which to insert
        Raises:
            KeyError: The specified position does not contain a letter
        """
        slots = self.layout[row][column]
        if not slots[0][0] and not slots[1][0]:
            raise KeyError('target position does not contain a letter')
        for slot, ind in slots:
            if slot:
                slot.set_letter(ind, letter)

    def rem_letter(self, row, column):
        """Removes a letter from a specified position.

        Notably, when using this method, if any slots at the specified position
        contain a word, the word will also be removed.

        Args:
            row: The row at which to insert
            column: The column at which to insert
        Raises:
            KeyError: The specified position does not contain a letter
        """
        slots = self.layout[row][column]
        if not slots[0][0] and not slots[1][0]:
            raise KeyError('target position does not contain a letter')
        for slot, ind in slots:
            if slot:
                slot.rem_letter(ind)

    def set_extra(self, *words):
        """Flags a word as an extra word when solving."""
        words = get_words(words)
        for word in words:
            self.extras.add(word)

    def rem_extra(self, *words):
        """Removes a word from the extras for solving."""
        words = get_words(words)
        for word in words:
            self.extras.discard(word)

    def set_word(self, word, row, col, direction=None):
        """Set a word into a slot.

        Args:
            word: The word to insert into the slot
            row: The row at which to insert
            col: The dolumn at which to insert
            direction: If the specified row and column contain more than one
                 slot, dir must be the directionality of the desired slot.
                 Otherwise, it is ignored
        Raises:
            ValueError: The target position contains more than one slot but the
                        direction was not specified
            KeyError: The target position does not contain any slots
        """
        slots = self[row, col]
        if len(slots) == 2 and direction is None:
            raise ValueError('direction not specified')
        if not slots:
            raise KeyError('target position does not contain a word')
        if not direction:
            slots[0].set_word(word)
        else:
            slots[direction].set_word(word)

    def rem_word(self, row, col, direction=None):
        """Remove a word from a slot.

        Args:
            row: The row at which to insert
            col: The dolumn at which to insert
            direction: If the specified row and column contain more than one
                 slot, dir must be the directionality of the desired slot.
                 Otherwise, it is ignored
        Raises:
            ValueError: The target position contains more than one slot but the
                        direction was not specified
            KeyError: The target position does not contain any slots
        """
        slots = self[row, col]
        if len(slots) == 2 and not direction:
            raise ValueError('direction not specified')
        if not slots:
            raise KeyError('target position does not contain a word')
        if not direction:
            slots[0].rem_word()
        else:
            slots[direction].rem_word()

    def solve(self,
              words,
              limit=None):
        """Fits words from the provided list into the Layout.

        Provided a dictionary of words indexed by size, fit them into the Layout
        while ensuring that there will be no conflicting overlaps.

        Args:
            words: Dictionary of words to use indexed by size
            limit: Optional.  Limit to the number of solutions which will be
                   found.  None indicates no limit.  Defaults to 10.
            maxstack: Optional.  Limit to the number of stack frames to use.
                      None indicates no limit.  Defaults to 100.
        Returns:
        A list of Solution objects.  Each solution found for the Layout will
            have a Solution object.
        Raises:
            KeyError: More slots of a specific length exist than words provided
                for that length.  No possible solutions exist as the Layout can
                never be completely filled.
            ValueError: Duplicate words detected in the Layout pre-solution.
        """
        from itertools import chain
        #Available words = words at length - used words
        #Available slots = slots - checked slots
        #Algo:
            #1. Get next slot
            #2. If no next, get a slot with fewest options
            #3. If no slots, append solution
            #4. Fill slot
            #5. Prioritize intersections
            #6. Solve intersections
            #7. Next word
            #8. Stop
        #First, turn the listings of words at each length into sets
        words = {k: set(v) for k, v in words.items()}
        for length in self.slots:
            if len(self.slots[length]) > len(words.get(length, [])):
                raise KeyError(('not enough {} letter words to fit the '
                                'available slots').format(length))
        #This is currently a recursive DFS.  To switch to BFS or djikstra,
        #change slot_stack from a list to a deque or priority queue.  It is not
        #known if there is a heuristic which can be used to prioritize the slots
        #for djikstra, though
        slot_stack, solutions, checked = [], [], set()
        used_words = set(self.extras)
        #Iterate through the slots and flag any that already have a word as
        #having been checked
        for slot in self.all_slots:
            if slot.has_word:
                if slot.word in used_words:
                    errstr = 'Duplicate word "{}" detected!'.format(slot.word)
                    raise ValueError(errstr)
                checked.add(slot)
                used_words.add(slot.word)
        #Define a function to get a Slot with the fewest number of possible
        #words left in the dictionary
        def get_fewest(open_slots):
            min_cnt = inf
            for slot in open_slots:
                words_left = len(words[len(slot)]-used_words)
                if words_left and words_left < min_cnt:
                    out = slot
                    min_cnt = words_left
            return out
        #Define a function to recursively solve the Layout
        def solve(indent=2):
            if limit is not None and len(solutions) >= limit:
                return
            #Find the open slots
            open_slots = self.all_slots - checked
            slot = None
            #If there are intersections to be processed
            if slot_stack:
                slot = slot_stack.pop()
                #Consume already checked Slots.  If none remain, break out.
                while slot in checked:
                    if not slot_stack:
                        slot = None
                        break
                    slot = slot_stack.pop()
            if not slot:
                #If there are open slots, get the one with the fewest words left
                if open_slots:
                    slot = get_fewest(open_slots)
                #If no open slots, log the solution and return
                else:
                    ext = set(chain.from_iterable(words.values())) - used_words
                    ext |= self.extras
                    solutions.append(Solution(self.layout, ext))
                    return
            #Get the remaining words that can fit into the slot
            slot_words = words[len(slot)] - used_words
            #Iterate through the remaining words
            for word in slot_words:
                #If the word can fit into the slot
                if slot.check_word(word):
                    #Log the word as used and the slot as checked
                    used_words.add(word)
                    checked.add(slot)
                    #Put the word into the slot
                    slot.set_word(word)
                    #Flag the overlaps for processing next
                    for other in slot.overlaps:
                        if other not in checked:
                            slot_stack.append(other)
                    #Recursively solve the next Slot
                    solve(indent+2)
                    #Remove the word from the used words and the slot from
                    #checked slots
                    used_words.discard(word)
                    checked.discard(slot)
                    #Remove the word from the Slot
                    slot.rem_word()
        #Start the recursive solution
        solve()
        #Return ALL the solutions
        return solutions


@export
class Solution(InstanceTracker):
    """Creates a Solution object to save off the current solution.

    Attributes:
        data: Array of lines in the solved layout
        data_vertical: Transposed version of data
        extra: The leftover "extra" words
    """
    def __init__(self, layout, extra=None):
        """Initializes a Solution object with the specified Layout object.

        Args:
            layout: The Layout object to utilize for reading the solution
            extra: Optional.  Any leftover words to include in the Solution.
                   Defaults to an empty list
        """
        self._layout = []
        self.data = ['']
        data_vertical = []
        #Log _layout as an alternative to the Layout object used, for internal
        #representation of the Solution object
        for row in layout:
            new_row = [' ']
            _layout = []
            for (rslot, rind), (dslot, dind) in row:
                if not rslot:
                    rslot, rind = [''], 0
                if not dslot:
                    dslot, dind = [''], 0
                let = rslot[rind] or dslot[dind] or ' '
                #Log the letter and the index 0 so that the Solution has all of
                #the data needed to construct an identical Solution
                _layout.append((let, 0))
                new_row.append(let)
            data_vertical.append(new_row)
            self.data.append(''.join(new_row))
            self._layout.append(_layout)
        self.data_vertical = ['']
        self.data_vertical.extend(' '+''.join(s) for s in zip(*data_vertical))
        self.data_vertical.append('')
        self.data.append('')
        try:
            self.extra = sorted(sorted(extra), key=len)
        except TypeError:
            self.extra = None

    def __repr__(self):
        """Returns an internal represntation of the Solution."""
        return 'Solution(layout={}, extra={})'.format(self._layout, self.extra)

    def disp(self, include_extra=True):
        """Yields lines in the provided layout with the letters filled in."""
        for line in self.data:
            yield line
        if self.extra and include_extra:
            yield 'Bonus words: {}'.format(', '.join(self.extra))

    def print(self, include_extra=True):
        """Prints the provided Layout with the letters filled in."""
        print('\n'.join(self.disp(include_extra)))


#Disable pylint flags: no value for cls argument (yeah, I'm using the hidden
#wrapper version which has an undocumented signature)
@_AUTO_ON.publish(refresh_method='refresh') #pylint: disable=no-value-for-parameter
@export
class Solver(InstanceTracker):
    """Creates a Solver to determine possible words and layouts.

    This object takes letters and an optional layout, as well as a spell checker
    and determines which words can be made using the provided letters, and, if a
    layout is provided, determines possible ways that the words could be laid
    out.

    Attributes:
        checker: The spell checker used to generate words
        layout: The layout of the word openings in matrix format
        letters: The letters used to create words
        maxlen: The largest word size which will be generated
        minlen: The smallest word size which will be generated
        words: Dictionary of words which can be made, ordered by length
    """
    def __init__(self,
                 checker,
                 letters=None,
                 layout=None,
                 lengths=(0, inf)):
        """Initializes a Solver object to find words and fit them into a layout.

        Args:
            checker: Spell checker used to build words
            letters: The letters to use to generate words
            layout: Optional.  The layout of letter openings in a grid format
            minlen: Optional.  The minimum word length to generate.  0 or less
                    gets changed to MIN_LEN.  Defaults to 0
            maxlen: Optional.  The maximum word length to generate.  Defaults to
                    infinite
        Raises:
            ValueError: The maximum length provided is less than the minimum
                length provided
        """
        self.checker = checker
        self.letters = letters
        self.layout = layout
        self._lengths = lengths
        self.solutions = []
        if lengths[0] < 1:
            lengths[0] = MIN_LEN
        #Check this after, so that __repr__ can be evaluated in an error trap
        #if an error occurs during __init__
        if lengths[1] < lengths[0]:
            raise ValueError('maximum length is less than minimum length')
        self._signature = None
        self.words = {}
        self.refresh()

    def __repr__(self):
        """Returns an internal representation for the object."""
        reprstr = 'Solver(letters={}, checker={}, layout={}, lengths={})'
        return reprstr.format(repr(self.letters),
                              repr(self.checker),
                              repr(self.layout),
                              repr(self._lengths))

    def print(self):
        """Prints the words in the Solver."""
        #Iterate through the words in key value pairs
        for length in sorted(self.words):
            words = self.words[length]
            #Sort in place - that way, future sorts don't suffer in efficiency
            words.sort()
            #Print the length, and then the words delimited by ", "
            print('{}: {}'.format(length, ', '.join(words)))

    def _refresh_words(self):
        from collections import Counter
        from itertools import chain, permutations
        from math import factorial
        words = {}
        if self.letters:
            count = len(self.letters)
            lengths = set(range(self.minlen, min(count, self.maxlen)+1))
            #nPr = n! / (n-r)!
            perm = sum(factorial(count)/factorial(count-num) for num in lengths)
            #If letter restrictions and number of permutations exceeds length of
            #dictionary, loop through dict to see which words can be built
            if perm > len(self.checker.words):
                avail = Counter(self.letters)
                for word in self.checker.words:
                    wordlen = len(word)
                    if wordlen in lengths and not Counter(word) - avail:
                        words.setdefault(wordlen, set()).add(word)
            #If letter restrictions and permutations < dictionary length, loop
            #through permutations to see which of them are words
            else:
                perms = chain.from_iterable(((i, ''.join(j))
                                             for j in permutations(self.letters,
                                                                   i))
                                            for i in lengths)
                for length, word in perms:
                    if self.checker.check_word(word):
                        words.setdefault(length, set()).add(word)
        #If no letter restrictions, grab all words within the length limits
        else:
            for word in self.checker.words:
                wordlen = len(word)
                if self.minlen <= wordlen <= self.maxlen:
                    words.setdefault(wordlen, set()).add(word)
        #Can sort keys and words here, but for speed, sort at print time
        self.words = {key: list(val) for key, val in words.items()}
        self._signature = _CHECKER_SIGNATURES[self.checker]


    def refresh(self):
        """Generates words which can be created.

        Used to re-compute possible words after updating the spell checker.
        """
        #Check the checker to see if it's been updated
        #If the checker has been updated, find all the words again
        if self._signature is not _CHECKER_SIGNATURES[self.checker]:
            self._refresh_words()
        if self.layout:
            self.solve(max(len(getattr(self, 'solutions', [])), 50))

    def solve(self, limit=None):
        """Fits possible words into the layout.

        Args:
            limit: Optional.  Limit to the number of solutions to find.  None
                   indicates no limit.  Defaults to None.
            maxstack: Optional.  Limit to the number of stack frames which will
                      be used while solving.  None indicates no limit.  Defaults
                      to None.

        Returns:
            A list of possible matrixes with words filled in such that there
            will be no conflicting letters and all letters will form words
        """
        self.solutions = self.layout.solve(self.words, limit)

    def print_solutions(self, num=None, include_extra=True):
        """Prints the provided number of solutions.

        Args:
            num: Optional.  The number of solutions to print.  None indicates
                 that all solutions are to be printed.  Defaults to None.
        """
        if num is None:
            for sol in self.solutions:
                sol.print(include_extra)
        else:
            for sol in self.solutions[:num]:
                sol.print(include_extra)

    @property
    def minlen(self):
        """Returns the minimum length of the Solver"""
        return self._lengths[0]

    @minlen.setter
    def minlen(self, newlen):
        """Sets the minimum length of the Solver"""
        if newlen > self._lengths[1]:
            raise ValueError('minimum length is more than maximum length')
        if newlen != self._lengths[0]:
            self._lengths = (newlen, self._lengths[1])
            self._signature = None
            self.refresh()

    @property
    def maxlen(self):
        """Returns the maximum length of the Solver"""
        return self._lengths[1]

    @maxlen.setter
    def maxlen(self, newlen):
        """Sets the maximum length of the Solver"""
        if newlen < self._lengths[0]:
            raise ValueError('maximum length is less than minimum length')
        if newlen != self._lengths[1]:
            self._lengths = (self._lengths[0], newlen)
            self._signature = None
            self.refresh()


@_AUTO_ON.auto_class('refresh', 'add', 'remove', test_method='_test')
@export
class Checker(InstanceTracker):
    """Creates a spell-checker to check that words are spelled correctly.

    Attributes:
        case: Boolean indicating the case sensitivity of the Checker
        words: Sorted list of the words in the Checker
    """
    def __init__(self, wordfile, encoding='utf8', case=False):
        """Initializes a Checker object with the specified word file.

        Args:
            wordfile: The name of the file to open
            encoding: Optional.  The encoding used by the wordfile.  Defaults to
                      utf-8
            case: Optional.  Boolean indicating the Checker's case sensitivity
        """
        self._wordfile = wordfile
        self._encoding = encoding
        self._words = None
        self._case = bool(case)
        _CHECKER_SIGNATURES[self] = None
        self.refresh()

    def __repr__(self):
        """Returns an internal represntation of the Checker."""
        return "Checker(wordfile='{}', encoding='{}', case={})".format(
            self._wordfile,
            self._encoding,
            self._case)

    def _test(self, solver):
        return self is getattr(solver, 'checker', None)

    def refresh(self):
        """Re-builds the word list from the word file."""
        words = set()
        with open(self._wordfile, encoding=self._encoding) as file:
            for line in file:
                if self._case:
                    words |= set(line.strip().split())
                else:
                    words |= set(i.lower() for i in line.strip().split())
        self._words = words
        _CHECKER_SIGNATURES[self] = object()

    def check_word(self, word):
        """Returns a boolean indicating whether a word is in the Checker."""
        if self._case:
            return word in self._words
        return word.lower() in self._words

    def check_pref(self, pref):
        """Returns a boolean indicating whether a prefix is in the Checker."""
        if not self._case:
            pref = pref.lower()
        for word in self._words:
            if word.startswith(pref):
                return True
        return False

    def add(self, *words):
        """Adds one or more words to the Checker and it's word file."""
        #Split out individual words
        words = get_words(words)
        with open(self._wordfile, 'r', encoding=self._encoding) as file:
            lines = file.readlines()
        #Convert to a set to remove duplicates, add in new words to set
        lines = set(' '.join(i.strip() for i in lines).split()) | words
        if self._case:
            self._words |= words
        else:
            self._words |= set(i.lower() for i in words)
        #Sort and write to the file
        with open(self._wordfile, 'w', encoding=self._encoding) as file:
            file.write('\n'.join(sorted(lines)))
        _CHECKER_SIGNATURES[self] = object()

    def remove(self, *words):
        """Removes one or more words from the Checker and it's word file."""
        #Split out individual words
        words = get_words(words)
        with open(self._wordfile, 'r', encoding=self._encoding) as file:
            lines = file.readlines()
        #Convert to a set to remove duplicates, remove target words from set
        lines = set(' '.join(i.strip() for i in lines).split())
        if self._case:
            self._words -= words
            lines -= words
        else:
            words = set(i.lower() for i in words)
            self._words -= words
            lines -= set(i for i in lines if i.lower() in words)
        #Sort and write to the file
        with open(self._wordfile, 'w', encoding=self._encoding) as file:
            file.write('\n'.join(sorted(lines)))
        _CHECKER_SIGNATURES[self] = object()

    @property
    def words(self):
        """Returns a set of words in the Checker."""
        #Let the other side take care of sorting the words
        #Still keep this as a property so that Checker.words can't be set
        return self._words

    @property
    def case(self):
        """Returns the case-sensitivity of the Checker."""
        return self._case

    @case.setter
    def case(self, value):
        """Sets the case-sensitivity of the Checker."""
        value = bool(value)
        if value != self._case:
            self._case = value
            self.refresh()


del _
