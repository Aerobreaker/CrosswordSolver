# CrosswordSolver

TODO:
Add google drive integration?


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
