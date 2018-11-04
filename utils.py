import os

def input_to_coords(user_input):
    """ Convert string input into src and dest coordinate pair
        Returns a list of two coordinate tuples
    """
    split_input = user_input.split(" ")
    # command = split_input[0]
    pos_1, pos_2 = split_input[1], split_input[2]
    return (pos_to_cord(pos_1), pos_to_cord(pos_2))


def pos_to_cord(pos_1):
    """ Convert locs to pair of coordinate tuples
    """
    return (ord(pos_1[0]) - ord('a'), int(pos_1[1]) - 1)


def _stringify_square(sq):
    if type(sq) is not str or len(sq) > 2:
        sq = sq.icon

    if len(sq) == 0:
        return '__|'
    if len(sq) == 1:
        return ' ' + sq + '|'
    if len(sq) == 2:
        return sq + '|'


def stringify_board(board):
    s = ''

    for row in range(len(board) - 1, -1, -1):
        s += '' + str(row + 1) + ' |'
        for col in range(0, len(board[row])):
            s += _stringify_square(board[col][row])
        s += os.linesep
    s += '    a  b  c  d  e' + os.linesep

    return s

def parse_test_case(path):
    f = open(path)
    line = f.readline()
    inital_board_state = []
    
    while line != '\n':
        piece, position = line.strip().split(' ')
        initial_board_state.append(dict(piece=piece, position=position))
        line = f.readline()
    line = f.readline().strip()
    upper_captures = [x for x in line[1:-1].split(' ') if x != '']
    line = f.readline().strip()
    lower_captures = [x for x in line[1:-1].split(' ') if x != '']
    line = f.readline()
    line = f.readline()
    moves = []
    while line != '':
        moves.append(line.strip())
        line = f.readline()

    return dict(initialPieces=inital_board_state, upperCaptures=upper_captures, lowerCaptures=lower_captures, moves=moves)