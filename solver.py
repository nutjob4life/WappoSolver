#!/usr/bin/env python
# encoding: utf-8

import sys, random

# specification = '''
# +-----------+
# |X         E|
# |      -    |
# |           |
# |      -   -|
# |      F    |
# |           |
# | |  W      |
# |-     -    |
# |  B Y  |   |
# |          -|
# | |       | |
# +-----------+
# '''

specification = '''
+-----------+
|X         E|
|      -    |
|           |
|      -   -|
|      F    |
|           |
| |         |
|-     -    |
|  B Y  |   |
|          -|
| |W      | |
+-----------+
'''

up, left, right, down = range(2, 9, 2)

class WappoException(Exception):
    pass
    
class KilledWappoException(WappoException):
    pass
    
class TeleportedException(WappoException):
    pass
    
class WappoEscapedException(WappoException):
    pass

class Pawn(object):
    def __init__(self, x, y):
        self.check(x, 'X')
        self.check(y, 'Y')
        self.x = x
        self.y = y
    
    def __repr__(self):
        return '%s(x=%d,y=%d)' % (self.__class__.__name__, self.x, self.y)
    
    def check(self, coord, name):
        if 0 <= coord <= 5:
            return
        raise ValueError('Illegal %s coordinate %d' % (name, coord))
    

class Wappo(Pawn):
    def __init__(self, x, y):
        super(Wappo, self).__init__(x, y)
    def __str__(self):
        return 'W'
    

class Blue(Pawn):
    def __init__(self, x, y):
        super(Blue, self).__init__(x, y)
    def __str__(self):
        return 'B'
    

class Teleporter(Pawn):
    def __init__(self, x, y):
        super(Teleporter, self).__init__(x, y)
    

class TeleportX(Teleporter):
    def __init__(self, x, y):
        super(TeleportX, self).__init__(x, y)
        self.other = None
    def __str__(self):
        return 'X'
    

class TeleportY(Teleporter):
    def __init__(self, x, y):
        super(TeleportY, self).__init__(x, y)
        self.other = None
    def __str__(self):
        return 'Y'
    

class Fire(Pawn):
    def __init__(self, x, y):
        super(Fire, self).__init__(x, y)
    def __str__(self):
        return 'F'
    

class Exit(Pawn):
    def __init__(self, x, y):
        super(Exit, self).__init__(x, y)
    def __str__(self):
        return 'E'
    

class Board(object):
    def __init__(self, text):
        self.objs = []
        for i in xrange(0, 6):
            row = []
            for j in xrange(0, 6):
                row.append([])
            self.objs.append(row)
        self.horizontals = []
        for i in xrange(0, 5):
            self.horizontals.append([False] * 6)
        self.verticals = []
        for i in xrange(0, 6):
            self.verticals.append([False] * 5)
        text = text.splitlines()[2:-1] # Get rid of top and bottom borders and blank line at top
        lines = []
        for line in text:
            lines.append(line[1:-1]) # Get rid of sides
        objLines = lines[::2]
        horizWallLines = lines[1::2]
        i = 0
        for line in horizWallLines:
            j = 0
            for char in line[::2]:
                if char == '-':
                    self.horizontals[i][j] = True
                j += 1
            i += 1
        i = 0
        for line in objLines:
            j = 0
            for char in line[::2]:
                if char == 'X':
                    self.teleportX = TeleportX(j, i)
                    self.objs[i][j].append(self.teleportX)
                elif char == 'Y':
                    self.teleportY = TeleportY(j, i)
                    self.objs[i][j].append(self.teleportY)
                elif char == 'E':
                    self.gameExit = Exit(j, i)
                    self.objs[i][j].append(self.gameExit)
                elif char == 'F':
                    self.fire = Fire(j, i)
                    self.objs[i][j].append(self.fire)
                elif char == 'W':
                    self.wappo = Wappo(j, i)
                    self.objs[i][j].append(self.wappo)
                elif char == 'B':
                    self.blue = Blue(j, i)
                    self.objs[i][j].append(self.blue)
                elif char == ' ':
                    pass
                else:
                    raise ValueError('Unknown pawn %s' % char)
                j += 1
            i += 1
        self.teleportX.other = self.teleportY
        self.teleportY.other = self.teleportX
        i = 0
        for line in objLines:
            j = 0
            for char in line[1::2]:
                if char == '|':
                    self.verticals[i][j] = True
                j += 1
            i += 1
    
    def move(self, pawn, direction):
        x, y = newX, newY = pawn.x, pawn.y
        if direction is up:
            if y == 0 or self.horizontals[y - 1][x]:
                return False
            newY -= 1
        elif direction is down:
            if y == 5 or self.horizontals[y][x]:
                return False
            newY += 1
        elif direction is left:
            if x == 0 or self.verticals[y][x - 1]:
                return False
            newX -= 1
        elif direction is right:
            if x == 5 or self.verticals[y][x]:
                return False
            newX += 1
        else:
            raise ValueError('Invalid direction %r' % direction)
        objects = self.objs[newY][newX]
        for obj in objects:
            if isinstance(obj, Teleporter):
                if pawn is self.fire:
                    return False
                destObjs = self.objs[obj.other.y][obj.other.y]
                if pawn is self.wappo and self.blue in destObjs:
                    return false
                if pawn is self.blue and self.wappo in destObjs:
                    raise KilledWappoException('Blue killed Wappo by teleporting to (%d, %d)'
                        % (obj.other.x, obj.other.y))
                self._move(pawn, obj.other.x, obj.other.y)
                raise TeleportedException('Teleported to (%d, %d)' % (pawn.x, pawn.y))
            if pawn is self.wappo:
                if obj is self.gameExit and self.fire not in objects:
                    raise WappoEscapedException('Wappo escaped by moving to (%d, %d)' % (newX, newY))
                if obj is self.fire:
                    if not self.move(self.fire, direction):
                        return False
                if obj is self.blue:
                    return False
            if pawn is self.blue:
                if obj is self.fire:
                    return False
                if obj is self.wappo:
                    raise KilledWappoException('Blue killed Wappo by moving to (%d, %d)' % (newX, newY))
        self._move(pawn, newX, newY)
        return True
        
    def _move(self, pawn, x, y):
        oldX, oldY = pawn.x, pawn.y
        self.objs[oldY][oldX].remove(pawn)
        pawn.x, pawn.y = x, y
        self.objs[y][x].append(pawn)
        
    def __str__(self):
        lines = []
        for row in self.objs:
            line = []
            for col in row:
                line.append(','.join([str(i) for i in col]))
            lines.append(' '.join(line))    
        return '\n'.join(lines)
    

def _dirSet(lastDirection):
    if lastDirection is None or lastDirection is up:
        return (up, right, down, left)
    elif lastDirection is right:
        return (right, down, left, up)
    elif lastDirection is down:
        return (down, left, up, right)
    elif lastDirection is left:
        return (left, up, right, down)
    else:
        raise ValueError('Unknown direction %r' % lastDirection)
    return directions
    

def _solve(moves, board, lastDirection=None):
    if len(moves) > 99:
        return False
    try:
        for direction in _dirSet(lastDirection):
            moves.append(direction)
            if board.move(board.wappo, direction):
                if _solve(moves, board, direction):
                    return True
                else:
                    moves.pop()
            else:
                moves.pop()
        return False
    except WappoEscapedException:
        return True
    except TeleportedException:
        return _solve(moves, board)
    except KilledWappoException:
        moves.pop()
        return False

def solve(board):
    moves = []
    if _solve(moves, board):
        return moves
    else:
        return None
    

if __name__ == '__main__':
    sys.setrecursionlimit(9999)
    board = Board(specification)
    moves = solve(board)
    if moves:
        print 'Solved in', len(moves), 'moves:'
        print moves
    else:
        print 'Insoluble.'

    