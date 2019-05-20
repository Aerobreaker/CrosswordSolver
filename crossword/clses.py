"""Create classes for use in crossword solvers."""
from gc import collect
from math import inf


from crossword.globs import _AUTO_ON, MIN_LEN, export
from crossword.funcs import group_count, get_words, BaseClass, Direction


__all__ = []


@export
class Slot(BaseClass):
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
        super().__init__()


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

    def check_word(self, word):
        """Checks to see if the specified word will fit in the Slot.

        Checks the overlaps with this slot to ensure that inserting the target
        word will not cause letter conflicts.

        Args:
            word: The word to check.
        Returns:
            Boolean indicating whether the word will cause conflicts
        """
        if len(word) != self.attributes[0] or self.has_word:
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

    def set_word(self, word, refresh=True):
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
        if len(word) != self.attributes[0]:
            raise AttributeError('target word is incorrect length')
        if self.has_word:
            raise TypeError('slot word is already set')
        self.word = word
        self.has_word = True
        if _AUTO_ON and refresh:
            collect()
            for solver in Solver.instances:
                if self in getattr(solver.layout, 'all_slots', set()):
                    solver.solve(max(len(getattr(solver, 'solutions', [])), 50))

    def rem_word(self, refresh=True):
        """Removes the stored word from the Slot, preserving any set letters."""
        self.has_word = False
        self.word = self._word
        if _AUTO_ON and refresh:
            collect()
            for solver in Solver.instances:
                if self in getattr(solver.layout, 'all_slots', set()):
                    solver.solve(max(len(getattr(solver, 'solutions', [])), 50))

    def set_letter(self, ind, let, refresh=True):
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
        if _AUTO_ON and refresh:
            collect()
            for solver in Solver.instances:
                if self in getattr(solver.layout, 'all_slots', set()):
                    solver.solve(max(len(getattr(solver, 'solutions', [])), 50))

    def rem_letter(self, ind, refresh=True):
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
        if _AUTO_ON and refresh:
            collect()
            for solver in Solver.instances:
                if self in getattr(solver.layout, 'all_slots', set()):
                    solver.solve(max(len(getattr(solver, 'solutions', [])), 50))

    def add_overlap(self, ind, other, other_ind):
        """Adds an overlap with the specified Slot.

        Args:
            ind: The index in this Slot where the overlap occurs
            other: The Slot which this Slot overlaps with
            other_ind: The index in other where the overlap occurs
        """
        self.overlaps[other] = other_ind
        other.overlaps[self] = ind

    def clear(self, refresh=True):
        """Removes the word and all letters from the Slot."""
        self.word = self._word = [''] * self.attributes[0]
        self._empty = self.attributes[0]
        self.has_word = False
        if _AUTO_ON and refresh:
            collect()
            for solver in Solver.instances:
                if self in getattr(solver.layout, 'all_slots', set()):
                    solver.solve(max(len(getattr(solver, 'solutions', [])), 50))


@export
class Layout(BaseClass):
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
        #For convenience, push all of the rows out to match the longest row
        length = max(len(row) for row in layout)
        for row_ind, row in enumerate(layout):
            if len(row) < length:
                layout[row_ind].extend([0]*(length-len(row)))
        self._layout = layout
        self.slots = {}
        self.extras = set()
        layout = []
        #Iterate through the rows groupwise, creating and logging Slots with a
        #right directionality
        for row_ind, row in enumerate(self._layout):
            row_slot = [[(None, 0), (None, 0)] for _ in range(length)]
            col_ind = 0
            for val, count in group_count(row):
                if val and count >= MIN_LEN:
                    slot = Slot(count, position=(row_ind, col_ind))
                    self.slots.setdefault(count, []).append(slot)
                    for i in range(count):
                        row_slot[col_ind+i][0] = (slot, i)
                col_ind += count
            layout.append(row_slot)
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
        super().__init__()

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
            row, column = key
            if abs(row) > len(self.layout):
                raise IndexError('row index out of range')
            if abs(column) > len(self.layout[row]):
                raise IndexError('column index out of range')
            if row < 0:
                row = len(self.layout) + row
            if column < 0:
                column = len(self.layout[row]) + column
            return self.layout[row][column]
        return self.layout[key]

    def clear(self):
        """Removes all words and letters from a Layout."""
        for slot in self.all_slots:
            slot.clear(False)
        if _AUTO_ON:
            collect()
            for solver in Solver.instances:
                if self is solver.layout:
                    solver.solve(len(getattr(solver, 'solutions', [])))

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
        slots = self[row, column]
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
        slots = self[row, column]
        if not slots[0][0] and not slots[1][0]:
            raise KeyError('target position does not contain a letter')
        for slot, ind in slots:
            if slot:
                slot.rem_letter(ind)

    def set_extra(self, word):
        """Flags a word as an extra word when solving."""
        self.extras.add(word)

    def rem_extra(self, word):
        """Removes a word from the extras for solving."""
        self.extras.discard(word)

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
        slot_stack = []
        checked = set()
        solutions = []
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
                words_left = len(words[slot.attributes[0]]-used_words)
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
                    solution = Solution(self.layout, ext)
                    solutions.append(solution)
                    return
            #Get the remaining words that can fit into the slot
            slot_words = words[slot.attributes[0]] - used_words
            #Iterate through the remaining words
            for word in slot_words:
                #If the word can fit into the slot
                if slot.check_word(word):
                    #Log the word as used and the slot as checked
                    used_words.add(word)
                    checked.add(slot)
                    #Put the word into the slot
                    slot.set_word(word, False)
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
                    slot.rem_word(False)
        #Start the recursive solution
        solve()
        #Return ALL the solutions
        return solutions


@export
class Solution(BaseClass):
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
        super().__init__()

    def __repr__(self):
        """Returns an internal represntation of the Solution."""
        return 'Solution(layout={}, extra={})'.format(self._layout, self.extra)

    def disp(self):
        """Yields lines in the provided layout with the letters filled in."""
        for line in self.data:
            yield line
        if self.extra:
            yield 'Bonus words: {}'.format(', '.join(self.extra))

    def print(self):
        """Prints the provided Layout with the letters filled in."""
        print('\n'.join(self.disp()))


#Disable pylint flags: no value for cls argument (yeah, I'm using the hidden
#wrapper version which has an undocumented signature)
@_AUTO_ON.publish(refresh_method='refresh') #pylint: disable=no-value-for-parameter
@export
class Solver(BaseClass):
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
        self._minlen, self._maxlen = lengths
        self.solutions = []
        if self._minlen < 1:
            self._minlen = MIN_LEN
        #Check this after, so that __repr__ can be evaluated in an error trap
        #if an error occurs during __init__
        if self._maxlen < self._minlen:
            raise ValueError('maximum length is less than minimum length')
        self.refresh()
        super().__init__()

    def __repr__(self):
        """Returns an internal representation for the object."""
        reprstr = 'Solver(letters={}, checker={}, layout={}, lengths={})'
        return reprstr.format(repr(self.letters),
                              repr(self.checker),
                              repr(self.layout),
                              (repr(self.minlen), repr(self.maxlen)))

    def print(self):
        """Prints the words in the Solver."""
        #Iterate through the words in key value pairs
        for length in sorted(self.words):
            words = self.words[length]
            #Sort in place - that way, future sorts don't suffer in efficiency
            words.sort()
            #Print the length, and then the words delimited by ", "
            print('{}: {}'.format(length, ', '.join(words)))

    def refresh(self):
        """Generates words which can be created.

        Used to re-compute possible words after updating the spell checker.
        """
        from collections import Counter
        from itertools import permutations
        from math import factorial
        words = {}
        if self.letters:
            count = len(self.letters)
            maxlen = min(count, self.maxlen)
            lengths = set(range(self.minlen, maxlen+1))
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
                for i in lengths:
                    for perm in permutations(self.letters, i):
                        word = ''.join(perm)
                        if self.checker.check_word(word):
                            words.setdefault(i, set()).add(word)
        #If no letter restrictions, grab all words within the length limits
        else:
            for word in self.checker.words:
                wordlen = len(word)
                if self.minlen <= wordlen <= self.maxlen:
                    words.setdefault(wordlen, set()).add(word)
        #Can sort keys and words here, but for speed, sort at print time
        self.words = {key: list(val) for key, val in words.items()}
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

    def print_solutions(self, num=None):
        """Prints the provided number of solutions.

        Args:
            num: Optional.  The number of solutions to print.  None indicates
                 that all solutions are to be printed.  Defaults to None.
        """
        if num is None:
            for sol in self.solutions:
                sol.print()
        else:
            for sol in self.solutions[:num]:
                sol.print()

    @property
    def minlen(self):
        """Returns the minimum length of the Solver"""
        return self._minlen

    @minlen.setter
    def minlen(self, newlen):
        """Sets the minimum length of the Solver"""
        if newlen > self._maxlen:
            raise ValueError('minimum length is more than maximum length')
        if newlen != self._minlen:
            self._minlen = newlen
            self.refresh()

    @property
    def maxlen(self):
        """Returns the maximum length of the Solver"""
        return self._maxlen

    @maxlen.setter
    def maxlen(self, newlen):
        """Sets the maximum length of the Solver"""
        if newlen < self._minlen:
            raise ValueError('maximum length is less than minimum length')
        if newlen != self._maxlen:
            self._maxlen = newlen
            self.refresh()


@export
class Checker(BaseClass):
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
        self.refresh()
        super().__init__()

    def __repr__(self):
        """Returns an internal represntation of the Checker."""
        return "Checker(wordfile='{}', encoding='{}', case={})".format(
            self._wordfile,
            self._encoding,
            self._case)

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
        if _AUTO_ON:
            collect()
            for solver in Solver.instances:
                if self is solver.checker:
                    solver.refresh()

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
        lines = set().union(*(set(i.strip().split()) for i in lines), words)
        if self._case:
            self._words |= words
        else:
            self._words |= set(i.lower() for i in words)
        #Sort and write to the file
        with open(self._wordfile, 'w', encoding=self._encoding) as file:
            file.write('\n'.join(sorted(lines)))
        if _AUTO_ON:
            collect()
            for solver in Solver.instances:
                if self is solver.checker:
                    solver.refresh()

    def remove(self, *words):
        """Removes one or more words from the Checker and it's word file."""
        #Split out individual words
        words = get_words(words)
        with open(self._wordfile, 'r', encoding=self._encoding) as file:
            lines = file.readlines()
        #Convert to a set to remove duplicates, remove target words from set
        lines = set().union(*(set(i.strip().split()) for i in lines))
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
        if _AUTO_ON:
            collect()
            for solver in Solver.instances:
                if self is solver.checker:
                    solver.refresh()

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
