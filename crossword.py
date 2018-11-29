from enum import auto, IntEnum, IntFlag


#Example usage:
#  PS C:\Python> py
#  Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)] on win32
#  Type "help", "copyright", "credits" or "license" for more information.
#  >>> import tst
#  >>>
#  >>> dictionary = tst.Checker('words.txt')
#  >>>
#  >>> board = tst.Layout(tst.layout1)
#  >>>
#  >>> solver = tst.Solver(dictionary, tst.letters1, board)
#  >>>
#  >>> solver.print()
#  3: gel, gen, gnu, gun, leg, lug, peg, pen, pug, pun
#  4: glen, glue, gulp, leng, luge, lung, plug
#  5: lunge
#  6: plunge
#  >>>
#  >>> solver.solve()
#  >>>
#  >>> for solution in solver.solutions[:3]:
#  ...     solution.print()
#  ...
#  
#      plunge
#    g u   u l
#    lug   l u
#    u     pun
#   peg      g
#     n   l  e
#    lung u
#    e  u g
#    glen e
#  
#  Bonus words: gel, gen, pen, leng, plug
#  
#      plunge
#    g u   u l
#    lug   l u
#    u     pun
#   peg      g
#     n   l  e
#    lung e
#    e  u n
#    glen g
#  
#  Bonus words: gel, gen, pen, luge, plug
#  
#      plunge
#    g u   u l
#    lug   l u
#    u     pun
#   peg      g
#     n   p  e
#    lung l
#    e  u u
#    glen g
#  
#  Bonus words: gel, gen, pen, leng, luge
#  >>>
#  >>> board[3,7][0][0].set_word('pun')
#  >>>
#  >>> board[6,4][1][0].set_word('gun')
#  >>>
#  >>> board.set_letter('u', 6, 6)
#  >>>
#  >>> solver.solve()
#  >>>
#  >>> for solution in solver.solutions:
#  ...     solution.print()
#  ...
#  
#      plunge
#    g u   u l
#    lug   l u
#    u     pun
#   peg      g
#     n   l  e
#    lung u
#    e  u g
#    glen e
#  
#  Bonus words: gel, gen, pen, leng, plug
#  
#      plunge
#    g u   u l
#    lug   l u
#    u     pun
#   leg      g
#     e   l  e
#    plug u
#    e  u g
#    glen e
#  
#  Bonus words: gen, gnu, pen, leng, lung
#  
#      plunge
#    g u   u l
#    lug   l u
#    u     pun
#   leg      g
#     e   l  e
#    plug u
#    e  u n
#    glen g
#  
#  Bonus words: gen, gnu, pen, leng, luge
#  
#      plunge
#    g u   u l
#    leg   l u
#    u     pun
#   peg      g
#     n   l  e
#    lung u
#    u  u g
#    glen e
#  
#  Bonus words: gel, gen, pen, leng, plug
#  
#      plunge
#    g e   u l
#    lug   l u
#    u     pun
#   leg      g
#     e   l  e
#    plug u
#    u  u g
#    glen e
#  
#  Bonus words: gen, gnu, pen, leng, lung
#  
#      plunge
#    g e   u l
#    lug   l u
#    u     pun
#   leg      g
#     e   l  e
#    plug u
#    u  u n
#    glen g
#  
#  Bonus words: gen, gnu, pen, leng, luge
#  >>>
#  >>> board.set_letter('n', 7, 6)
#  >>>
#  >>> board[2,1][0][0].set_word('lug')
#  >>>
#  >>> solver.solve()
#  >>>
#  >>> for solution in solver.solutions:
#  ...     solution.print()
#  ...
#  
#      plunge
#    g u   u l
#    lug   l u
#    u     pun
#   leg      g
#     e   l  e
#    plug u
#    e  u n
#    glen g
#  
#  Bonus words: gen, gnu, pen, leng, luge
#  
#      plunge
#    g e   u l
#    lug   l u
#    u     pun
#   leg      g
#     e   l  e
#    plug u
#    u  u n
#    glen g
#  
#  Bonus words: gen, gnu, pen, leng, luge
#  >>>


#This one has TONS of solutions.  Like thousands.  Because there are so many
#overlapping 3-letter words
#556 - Flora -> Seed 12
#Further investigation has revealed that there are 58296 solutions
layout0 = [[0,0,0,1,1,1,1,0,0,0,0],
          [0,0,0,0,0,0,1,0,0,0,0],
          [0,0,1,0,1,1,1,1,1,1,0],
          [0,1,1,1,1,0,1,0,0,0,0],
          [0,0,1,0,1,0,0,0,1,1,1],
          [1,1,1,0,1,0,0,0,1,0,1],
          [0,1,0,0,0,0,1,0,1,0,1],
          [0,1,0,0,0,0,1,1,1,0,0],
          [1,1,1,0,1,1,1,0,0,0,0],
          [1,0,1,1,1,0,0,0,0,0,0],
          [1,1,1,0,1,0,0,0,0,0,0]]
letters0 = 'revamp'
#Examples:
layout1 = [[0,0,0,1,1,1,1,1,1,0],
           [0,1,0,1,0,0,0,1,0,1],
           [0,1,1,1,0,0,0,1,0,1],
           [0,1,0,0,0,0,0,1,1,1],
           [1,1,1,0,0,0,0,0,0,1],
           [0,0,1,0,0,0,1,0,0,1],
           [0,1,1,1,1,0,1,0,0,0],
           [0,1,0,0,1,0,1,0,0,0],
           [0,1,1,1,1,0,1,0,0,0]]
letters1 = 'plunge'
layout2 = [[0,0,1,0,0,0,0,0,0,0,1],
           [0,0,1,0,0,0,0,0,1,0,1],
           [0,0,1,0,0,1,0,0,1,0,1],
           [0,0,1,1,1,1,0,0,1,1,1],
           [1,1,1,0,0,1,1,1,1,0,0],
           [1,0,0,0,0,1,0,0,1,0,0],
           [1,1,1,0,0,0,0,0,1,0,0],
           [0,0,1,0,1,0,1,1,1,0,0],
           [0,1,1,1,1,0,1,0,0,0,0],
           [0,0,0,0,1,1,1,0,0,0,0]]
letters2 = 'fiction'
layout3 = [[0,1,1,1,1,0,0],
           [0,1,0,0,1,0,0],
           [1,1,1,0,1,1,1],
           [0,0,1,0,0,1,0],
           [1,1,1,1,1,1,0],
           [1,0,0,0,0,0,0],
           [1,0,0,0,0,0,0]]
letters3 = 'candid'
#
#1: 206 - Sky -> Dusk 14
#    PLUNGE
#  G U   U L
#  LUG   L U
#  U     PUN
# LEG      G
#   E   L  E
#  PLUG U
#  E  U N
#  GLEN G
#
#2: 546 - Flora -> Seed 2
#   T       C
#   O     F O
#   N  I  I I
#   ICON  CON
# TIC  FONT
# O    O  I
# NIT     O
#   I I FIN
#  INTO I
#     NOT
#
#3: 547 - Flora -> Seed 3
#  ACID
#  I  I
# ADD DAD
#   I  N
# CANDID
# A
# D



def group_count(iterable):
    """Groups an iterable by values and counts the lengths of the groups."""
    from itertools import groupby
    #Groupby splits it into groups.  But the items consists of each individual
    #element in the group.  So convert to a list and read the length of said
    #list
    for grp, items in groupby(iterable):
        yield grp, len(list(items))
#


def prep(iterable):
    return [[int(j) for j in i] for i in iterable]
#


class Direction(IntEnum):
    """Enumerator to indicate right or down direction."""
    RIGHT = 0
    DOWN = auto()
#


class Debug(IntFlag):
    NONE = 0
    VARS = auto()
    SOLUTIONS = auto()
#


class Slot(object):
    """Creates a slot to track an opening to put a word into.
    
    This object is created as a helper to the Layout object.  It tracks
    location, length, and direction of a word slot.  Notably, it's possible to
    have two words which wholly overlap as long as they're different lengths.
    
    Attributes:
        direction: The direction of the word (Direction.DOWN / Direction.RIGHT)
        has_word: Boolean indicating whether or not the Slot has a word assigned
        overlaps: Dictionary of overlapping slots
        position: The (row, column) that the word starts on
        size: The length of the word
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
        self.size = size
        self.position = position
        self.direction = direction
        self.overlaps = {}
        self.word = self._word = [''] * size
        self._empty = size
        self.has_word = False
    
    def __repr__(self):
        """Returns an internal representation of a Slot object."""
        return ('Slot(size={}, position={}, direction={})'.format(
            self.size, self.position, self.direction)
        )
    
    #__hash__ and __eq__ are used to identify an object.  Two objects are
    #considered duplicates if the hashes are the same and they compare equal to
    #one another.
    
    def __hash__(self):
        """Returns a hash for the Slot object."""
        return hash((self.size, self.position, self.direction))
    
    def __eq__(self, other):
        """Returns true if equal to other."""
        return (self.size, self.position, self.direction) == other
    
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
        if len(word) != self.size or self.has_word:
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
        if len(word) != self.size:
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
        self.word = self._word = [''] * self.size
        self._empty = self.size
        self.has_word = False
#


class Layout(object):
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
        #For convenience, push all of the rows out to match the longest row
        length = len(max(layout, key=len))
        for ind, row in enumerate(layout):
            rowlen = len(row)
            if rowlen < length:
                layout[ind].extend([0]*(length-rowlen))
        self._layout = layout
        transposed = zip(*layout)
        slots = {}
        row_slots = []
        #Iterate through the rows groupwise, creating and logging Slots with a
        #right directionality
        for row_ind, row in enumerate(layout):
            row_slot = [[(None, 0), (None, 0)] for _ in range(len(row))]
            col_ind = 0
            for val, count in group_count(row):
                if val and count > 2:
                    slot = Slot(count, position=(row_ind, col_ind))
                    slots.setdefault(count, []).append(slot)
                    for i in range(count):
                        row_slot[col_ind+i][0] = (slot, i)
                col_ind += count
            row_slots.append(row_slot)
        #Iterate through the columns groupwise, creating and logging Slots with
        #a down directionality
        for col_ind, col in enumerate(transposed):
            row_ind = 0
            for val, count in group_count(col):
                if val and count > 2:
                    slot = Slot(count,
                                position=(row_ind, col_ind),
                                direction=Direction.DOWN
                               )
                    slots.setdefault(count, []).append(slot)
                    for i in range(count):
                        over_slot, over_ind = row_slots[row_ind+i][col_ind][0]
                        if over_slot:
                            slot.add_overlap(i, over_slot, over_ind)
                        row_slots[row_ind+i][col_ind][1] = (slot, i)
                row_ind += count
        #Save off the dict of slots and the layout of slots
        self.slots = slots
        self.layout = row_slots
    
    def __repr__(self):
        """Returns an internal represntation of the Layout."""
        return 'Layout(layout={})'.format(self._layout)
    
    def __getitem__(self, key):
        """Gets the slots at the specified position.
        
        Args:
            key: The key to get
        Raises:
            IndexError: row or column is outside the bounds of the layout
        """
        if hasattr(key, '__iter__'):
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
        else:
            return self.layout[key]
    
    def clear(self):
        """Removes all words and letters from a Layout."""
        from itertools import chain
        for slot in chain.from_iterable(self.slots.values()):
            slot.clear()
    
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
    
    def solve(self,
              words,
              limit=None,
              maxstack=None,
              debug=Debug.NONE,
              filename=''):
        """Fits words from the provided list into the Layout.
        
        Provided a dictionary of words indexed by size, fit them into the Layout
        while ensuring that there will be no conflicting overlaps.
        
        Args:
            words: Dictionary of words to use indexed by size
            limit: Optional.  Limit to the number of solutions which will be
                   found.  None indicates no limit.  Defaults to 10.
            maxstack: Optional.  Limit to the number of stack frames to use.
                      None indicates no limit.  Defaults to 100.
            debug: Optional.  Debug flag.  Defaults to False
            filename: Optional.  Filename to write debug logs to.  Defaults to
                      a null string.  If empty, turns off the debug flag
        Returns:            A list of Solution objects.  Each solution found for the Layout will
            have a Solution object.
        Raises:
            KeyError: More slots of a specific length exist than words provided
                for that length.  No possible solutions exist as the Layout can
                never be completely filled.
        """
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
        from itertools import chain
        
        if debug and not filename:
            debug = Debug.NONE
        
        #First, turn the listings of words at each length into sets
        words = {k: set(v) for k, v in words.items()}
        for length in self.slots:
            if len(self.slots[length]) > len(words.get(length, [])):
                raise KeyError(('not enough {} letter words to fit the '
                                'available slots').format(length))
        used_words = set()
        slot_stack = []
        checked = set()
        #Store all slots into a single set
        slots = set(chain.from_iterable(self.slots.values()))
        solutions = []
        run_once = True
        #Iterate through the slots and flag any that already have a word as
        #having been checked
        for slot in slots:
            if slot.has_word:
                checked.add(slot)
                used_words.add(slot.word)
        #Define a function to get a Slot with the fewest number of possible
        #words left in the dictionary
        def get_fewest(slots):
            min_cnt = float('inf')
            for slot in slots:
                words_left = len(words[slot.size]-used_words)
                if words_left and words_left < min_cnt:
                    out = slot
                    min_cnt = words_left
            return out
        #Define a function to write debug logs to a file
        def fwrite(text, indent):
            nonlocal run_once
            if indent:
                lev = indent // 2
            else:
                lev = ''
            #Blanks the file and prevents writing a blank line at the beginning
            if run_once:
                run_once = False
                with open(filename, 'w') as file:
                    file.write('')
                if not text:
                    return
            with open(filename, 'a') as file:
                if text:
                    file.write('{:<{ind}}{}\n'.format(lev, text, ind=indent))
                else:
                    file.write('\n')
        #Define a function to recursively solve the Layout
        def solve(stacklev, indent=2):
            if ((maxstack is not None and stacklev >= maxstack)
                or (limit is not None and len(solutions) >= limit)):
                return
            #Find the open slots
            open_slots = slots - checked
            #DEBUG CODE
            lev = indent // 2
            if Debug.VARS in debug:
                fwrite('', indent)
                fwrite('Before:', indent)
                fwrite('  Words: {}'.format(words), indent)
                fwrite('  Used_words: {}'.format(used_words), indent)
                fwrite('  Slot_stack: {}'.format(slot_stack), indent)
                fwrite('  Checked: {}'.format(checked), indent)
                fwrite('  Slots: {}'.format(open_slots), indent)
                fwrite('  Solutions: {}'.format(solutions), indent)
            #END DEBUG CODE
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
                    solution = Solution(self.layout, ext)
                    solutions.append(solution)
                    #DEBUG CODE
                    if Debug.SOLUTIONS in debug:
                        if Debug.VARS in debug:
                            fwrite('Solution:', indent)
                            for line in solution.disp():
                                fwrite('  {}'.format(line), indent)
                        else:
                            fwrite('Solution:', 0)
                            for line in solution.disp():
                                fwrite('  {}'.format(line), 0)
                    #END DEBUG CODE
                    return
            #Get the remaining words that can fit into the slot
            slot_words = words[slot.size] - used_words
            #DEBUG CODE
            if Debug.VARS in debug:
                fwrite('    Slot: {}'.format(slot), indent)
                fwrite('    Slot words: {}'.format(slot_words), indent)
            #END DEBUG CODE
            #Iterate through the remaining words
            for word in slot_words:
                #DEBUG CODE
                if Debug.VARS in debug:
                    fwrite('  Checking {}: {}'.format(word,
                                                      slot.check_word(word)
                                                     ),
                           indent
                          )
                #END DEBUG CODE
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
                    solve(stacklev+1, indent+2)
                    #Remove the word from the used words and the slot from
                    #checked slots
                    used_words.discard(word)
                    checked.discard(slot)
                    #Remove the word from the Slot
                    slot.rem_word()
            #DEBUG CODE
            if Debug.VARS in debug:
                fwrite('After:', indent)
                fwrite('  Words: {}'.format(words), indent)
                fwrite('  Used_words: {}'.format(used_words), indent)
                fwrite('  Slot_stack: {}'.format(slot_stack), indent)
                fwrite('  Checked: {}'.format(checked), indent)
                fwrite('  Slots: {}'.format(slots), indent)
                fwrite('  Solutions: {}'.format(solutions), indent)
                fwrite('', indent)
            #END DEBUG CODE
        #Start the recursive solution
        solve(0)
        #Return ALL the solutions
        return solutions
#


class Solution(object):
    """Creates a Solution object to save off the current solution.
    
    Attributes:
        data: Array of lines in the solved layout
        data_vertical: Transposed version of data
        extra: The leftover "extra" words
    """
    
    def __init__(self, layout, extra = None):
        """Initializes a Solution object with the specified Layout object.
        
        Args:
            layout: The Layout object to utilize for reading the solution
            extra: Optional.  Any leftover words to include in the Solution.
                   Defaults to an empty list
        """
        self.data = ['']
        data_vertical = []
        #Log _layout as an alternative to the Layout object used, for internal
        #representation of the Solution object
        self._layout = []
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
        self.extra = extra
    
    def __repr__(self):
        """Returns an internal represntation of the Solution."""
        return 'Solution(layout={}, extra={})'.format(self._layout, self.extra)
    
    def disp(self):
        """Yields lines in the provided layout with the letters filled in."""
        for line in self.data:
            yield line
        if self.extra:
            extra = sorted(sorted(self.extra), key=len)
            yield 'Bonus words: {}'.format(', '.join(extra))
    
    def print(self):
        """Prints the provided Layout with the letters filled in."""
        print('\n'.join(self.disp()))


class Solver(object):
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
        slots: Slots which can hold words, ordered by size
        words: Dictionary of words which can be made, ordered by length
    """

    def __init__(self, checker, letters=None, layout=None, minlen=3, maxlen=0):
        """Initializes a Solver object to find words and fit them into a layout.

        Args:
            checker: Spell checker used to build words
            letters: The letters to use to generate words
            minlen: Optional.  The minimum word length to generate.  Defaults to
                    three
            maxlen: Optional.  The maximum word length to generate.  Defaults to
                    the number of provided letters
            layout: Optional.  The layout of letter openings in a grid format
        """
        self.checker = checker
        self.letters = letters
        self.minlen = minlen
        self.maxlen = maxlen
        if letters and self.maxlen <= self.minlen:
            self.maxlen = len(letters) + 1
        self.refresh()
        self.layout = layout
        if layout:
            self.solve(limit=10, maxstack=100)

    def __repr__(self):
        """Returns an internal representation for the object."""
        return ("Solver(letters='{}', checker={}, layout={}, minlen={}, "
                "maxlen={})").format(self.letters,
                                     self.checker,
                                     self.layout,
                                     self.minlen,
                                     self.maxlen)

    def print(self):
        """Prints the words in the Solver."""
        #Iterate through the words in key value pairs
        for length, words in self.words.items():
            #Print the length, and then the words delimited by ", "
            print('{}: {}'.format(length, ', '.join(words)))

    def refresh(self):
        """Generates words which can be created.

        Used to re-compute possible words after updating the spell checker.
        """
        from itertools import permutations
        self.words = {}
        #Go through all possible permutations of letters from the min length to
        #the max length.  If they make a word in the Checker, add it to the word
        #list.
        if self.letters:
            for i in range(self.minlen, self.maxlen):
                words = set()
                for p in permutations(self.letters, i):
                    word = ''.join(p)
                    if self.checker.check_word(word):
                        words.add(word)
                if words:
                    self.words[i] = sorted(words)
        else:
            for word in self.checker.words:
                self.words.setdefault(len(word), []).append(word)

    def solve(self, limit=None, maxstack=None):
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
        self.solutions = self.layout.solve(self.words, limit, maxstack)
#


class Checker(object):
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
        self.case = case

    def __repr__(self):
        """Returns an internal represntation of the Checker."""
        return "Checker(wordfile='{}', encoding='{}', case={})".format(
            self._wordfile,
            self._encoding,
            self._case
        )

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

    def _getwords(self, words):
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
        words = chain.from_iterable(i.split() for i in words)
        #Join the previously split arrays, then split out on a different
        #delimiter.  Ignore empty sub-strings
        return set(i for i in ','.join(words).split(',') if i)

    def check_word(self, word):
        """Returns a boolean indicating whether a word is in the Checker."""
        if self._case:
            return word.lower() in self._words
        return word in self._words

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
        words = self._getwords(words)
        with open(self._wordfile, 'r', encoding=self._encoding) as file:
            lines = file.readlines()
        #Convert to a set to remove duplicates, add in new words to set
        lines = set(i.strip() for i in lines) | words
        if self._case:
            self._words |= words
        else:
            self._words |= set(i.lower() for i in words)
        #Sort and write to the file
        with open(self._wordfile, 'w', encoding=self._encoding) as file:
            file.write('\n'.join(sorted(lines)))

    def remove(self, *words):
        """Removes one or more words from the Checker and it's word file."""
        #Split out individual words
        words = self._getwords(words)
        with open(self._wordfile, 'r', encoding=self._encoding) as file:
            lines = file.readlines()
        #Convert to a set to remove duplicates, remove target words from set
        lines = set(i.strip() for i in lines)
        if self._case:
            self._words -= words
            lines -= set(i for i in lines if i in words)
        else:
            self._words -= set(i.lower() for i in words)
            lines -= set(i for i in lines if i.lower() in words)
        #Sort and write to the file
        with open(self._wordfile, 'w', encoding=self._encoding) as file:
            file.write('\n'.join(sorted(lines)))

    @property
    def words(self):
        """Returns a sorted set of words in the Checker."""
        return sorted(self._words)

    @property
    def case(self):
        return self._case

    @case.setter
    def case(self, value):
        self._case = bool(value)
        self.refresh()
#


d = Checker('words.txt')
l1 = Layout(layout1)
s1 = Solver(d, letters1, l1)
l2 = Layout(layout2)
s2 = Solver(d, letters2, l2)
l3 = Layout(layout3)
s3 = Solver(d, letters3, l3)