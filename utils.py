import os

def input_to_coords(user_input):
    """ Parse user input into src and dest coordinate pair
        Returns a list of two coordinate tuples
    """
    split_input = user_input.split(" ")
    pos_1, pos_2 = split_input[1], split_input[2]
    return (pos_to_coords(pos_1), pos_to_coords(pos_2))

def input_to_drop(user_input):
    split_input = user_input.split(" ")
    piece, dst = split_input[1], split_input[2]
    return piece, pos_to_coords(dst)

def input_to_commands(user_input):
    """ Parse user input into move or drop command and promote command
    """
    split_input = user_input.split(" ")
    command = split_input[0]
    if len(split_input) == 4:
        return (command, True)
    return (command, False)

def pos_to_coords(pos_1):
    """ Convert board position to grid coordinates
    """
    return (ord(pos_1[0]) - ord('a'), int(pos_1[1]) - 1)

def coords_to_pos(coords):
    """ Convert grid coordinates to board position
    """
    return chr(ord('a') + coords[0]) + str(coords[1] + 1)

def add_coords(player, coord_1, coord_2):
    """ Adds two coordinate pairs by row, col values
    """
    if player.name == "lower":
        return (coord_1[0] + coord_2[0], coord_1[1] + coord_2[1])
    return (coord_1[0] + coord_2[0], coord_2[1] - coord_1[1])

def get_moves_from_dict(moves_dict):
    moves = []
    for icon, coord in moves_dict:
        for dst in moves_dict[(icon, coord)]:
            move_string = "move "
            move_string += coords_to_pos(coord) + " "
            move_string += dst
            moves.append(move_string)
    return moves

def get_drops_from_dict(drops_dict):
    drops = []
    for icon in drops_dict:
        for dst in drops_dict[icon]:
            drop_string = "drop "
            drop_string += icon.lower() + " "
            drop_string += dst
            drops.append(drop_string)
    return drops

def _stringify_square(sq):
    if type(sq) is int:
        sq = str(sq) 

    elif type(sq) is not str:
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
    s += '    ' + '  '.join([chr(ord('a') + i) for i in range(len(board))]) + os.linesep

    return s

def parse_test_case(path):
    f = open(path)
    line = f.readline()
    initial_board_state = []
    
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

    return dict(initialPieces=initial_board_state, upperCaptures=upper_captures, lowerCaptures=lower_captures, moves=moves)