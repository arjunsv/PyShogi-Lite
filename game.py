from utils import input_to_coords, input_to_commands, stringify_board
from utils import add_coords, coords_to_pos, pos_to_coord, input_to_drop
import os, sys
import time
import traceback
import ast
import copy
import argparse


class Player:

    def __init__(self, name, heatmap, captures, king):
        self.name = name
        self.heatmap = heatmap
        self.captures = captures
        self.king = king

class Piece:

    def __init__(self, player, coords, icon, blockable):
        """ Initializes piece
        """
        self.player = player
        self.coords = coords
        self.icon = icon
        self.blockable = blockable

        if self.player == "lower":
            self.icon = self.icon.lower()

    def make_copy(self):
        piece_type = type(self)
        copy = piece_type(self.player, self.coords)
        return copy

    def __eq__(self, other):
        return type(self) == type(other) and self.player == other.player and \
               self.blockable == other.blockable and self.coords == other.coords 


class King(Piece):

    blockable_moves_sets = []
    unblockable_moves = [(-1, 1), (0, 1), 
                         (1, 1), (1, 0), 
                         (1, -1), (0, -1), 
                         (-1, -1), (-1, 0)]

    def __init__(self, player, coords):
        super().__init__(player, coords, "K", False)

    def promote(self):
        print("King cannot be promoted.")


class GoldGeneral(Piece):

    blockable_moves_sets = []
    unblockable_moves = [(-1, 1), (0, 1), 
                         (1, 1), (1, 0), 
                         (0, -1), (-1, 0)]

    def __init__(self, player, coords):
        super().__init__(player, coords, "G", False)

    def promote(self):
        print("Gold General cannot be promoted.")


class SilverGeneral(Piece):

    blockable_moves_sets = []
    unblockable_moves = [(-1, 1), (0, 1), 
                         (1, 1), (1, -1), 
                         (-1, -1)]

    def __init__(self, player, coords):
        super().__init__(player, coords, "S", False)

    def promote(self):
        self.icon = "+" + self.icon
        self.unblockable_moves = GoldGeneral.unblockable_moves


class Bishop(Piece):

    up_right_moves = [(1, 1), (2, 2), (3, 3), (4, 4)]
    down_right_moves = [(1, -1), (2, -2), (3, -3), (4, -4)]
    down_left_moves = [(-1, -1), (-2, -2), (-3, -3), (-4, -4)]
    up_left_moves = [(-1, 1), (-2, 2), (-3, 3), (-4, 4)]

    blockable_moves_sets = [up_right_moves, down_left_moves, up_left_moves]
    unblockable_moves = []

    def __init__(self, player, coords):
        super().__init__(player, coords, "B", True)

    def promote(self):
        self.icon = "+" + self.icon
        self.unblockable_moves.extend(King.unblockable_moves)


class Rook(Piece):

    up_moves = [(0, 1), (0, 2), (0, 3), (0, 4)]
    right_moves = [(1, 0), (2, 0), (3, 0), (4, 0)]
    down_moves = [(0, -1), (0, -2), (0, -3), (0, -4)]
    left_moves = [(-1, 0), (-2, 0), (-3, 0), (-4, 0)]

    unblockable_moves = []
    blockable_moves_sets = [up_moves, right_moves, down_moves, left_moves]

    def __init__(self, player, coords):
        self.icon = "R"
        super().__init__(player, coords, "R", True)

    def promote(self):
        self.icon = "+" + self.icon
        self.unblockable_moves.extend(King.unblockable_moves)


class Pawn(Piece):

    unblockable_moves = [(0, 1)]
    blockable_moves_sets = []

    def __init__(self, player, coords):
        self.icon = "P"
        super().__init__(player, coords, "P", False)

    def promote(self):
        self.icon = "+" + self.icon
        self.unblockable_moves = GoldGeneral.unblockable_moves


class Board:

    def __init__(self, filename):
        """ Initializes board.
        """
        self.BOARD_SIZE = 5
        self.grid = [[""]*self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        self.heatmap_UPPER = [[0]*self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        self.heatmap_lower = [[0]*self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        self.blockable_pieces = []
        self.king_UPPER = None
        self.king_lower = None
        self.captures_UPPER = []
        self.captures_lower = []
        self.pieces_UPPER = []
        self.pieces_lower = []
        self.current_player = "lower"
        self.game_over = False
        self.num_moves = 0

        if filename:
            self.init_grid_filemode(filename)
        else:
            self.init_grid()


    def init_grid(self):
        """ Populates pieces of initial board state.
        """
        pieces = [King, GoldGeneral, SilverGeneral, Bishop, Rook]

        for i in range(self.BOARD_SIZE):

            piece_UPPER = pieces[i]("UPPER", (4 - i, 4))
            piece_lower = pieces[i]("lower", (i, 0))

            self.place_piece(piece_UPPER, piece_UPPER.coords)
            self.place_piece(piece_lower, piece_lower.coords)

        self.place_piece(Pawn("UPPER", (4, 3)), (4, 3))
        self.place_piece(Pawn("lower", (0, 1)), (0, 1))


    def init_grid_filemode(self, filename):
        """ Initializes grid from file config as opposed to default config.
        """
        with open(filename) as f:
            self.read_file_lines(f.readlines())
    
    def read_file_lines(self, lines):
        icon_to_piece = {'k': King, 'g': GoldGeneral, 's': SilverGeneral, 
                         'b': Bishop, 'r': Rook, 'p': Pawn}

        is_upper = True
        
        for line in lines:

            # Pieces
            if line[0].lower() in icon_to_piece:
                player = "UPPER" if line[0].isupper() else "lower"
                position = line[2:4]
                piece = icon_to_piece[line[0].lower()](player, pos_to_coord(position))
                self.place_piece(piece, pos_to_coord(position))

            # Captured Pieces
            if line[0] == "[" and is_upper:
                is_upper = False

                # TODO: Need to put the actual pieces in there.. not just the icons
                self.captures_UPPER = ast.literal_eval(line)

            if line[0] == "[" and not is_upper:
                self.captures_lower = ast.literal_eval(line)    

            # Commands
            if line[0:4] == "move" or line[0:4] == "drop":
                self.execute_input(line)

            
    def copy_board(self):
        """ Returns a new board object that is a copy of the current instance (self)
        """
        new_board = Board()
        new_board.BOARD_SIZE = self.BOARD_SIZE
        new_board.grid = copy.deepcopy(self.grid)
        new_board.heatmap_UPPER = copy.deepcopy(self.heatmap_UPPER)
        new_board.heatmap_lower = copy.deepcopy(self.heatmap_lower)
        new_board.blockable_pieces = [bp.make_copy() for bp in self.blockable_pieces]
        new_board.king_UPPER = self.king_UPPER.make_copy()
        new_board.king_lower = self.king_lower.make_copy()
        new_board.captures_UPPER = [cp.make_copy() for cp in self.captures_UPPER]
        new_board.captures_lower = [cp.make_copy() for cp in self.captures_lower]
        new_board.pieces_UPPER = [p.make_copy() for p in self.pieces_UPPER]
        new_board.pieces_lower = [p.make_copy() for p in self.pieces_lower]
        new_board.current_player = self.current_player

        return new_board


    def execute_input(self, user_input):
        command, promote = input_to_commands(user_input)

        # Execute move command
        if command == "move":
            src, dst = input_to_coords(user_input)
            piece = self.get_piece(src)
            if self.move_piece(src, dst):
                if promote and self.can_promote(piece.player, dst):
                    piece.promote()
                self.switch_current_player()
                self.num_moves += 1
                print(piece.player + " player action: " + user_input.strip())
                return True
            else:
                print("Invalid move.")
                return False

        elif command == "drop":
            icon, dst = input_to_drop(user_input)
            self.drop_piece(icon, pos_to_coord(dst))
            self.switch_current_player()
            print(piece.player + " player action: " + user_input.strip()) 
            return True

        return False

    def get_valid_dsts(self, coords, count_self=False):
        """ returns all valid destinations a piece can move to.
        """

        valid_dsts = []
        piece = self.get_piece(coords)

        for move in piece.unblockable_moves:
            possible_dst = add_coords(self.current_player, move, coords)
            if self.in_bounds(possible_dst):
                if not self.is_players_piece(piece.player, possible_dst) or count_self:
                    # Can't move King into check
                    opp_heatmap = self.heatmap_lower if piece.player == "UPPER" else self.heatmap_UPPER
                    if type(piece) == King and opp_heatmap[possible_dst[0]][possible_dst[1]] > 0:
                        pass
                    else:
                        valid_dsts.append(possible_dst)

        for moves_set in piece.blockable_moves_sets:
            for move in moves_set:
                possible_dst = add_coords(self.current_player, move, coords)

                if self.in_bounds(possible_dst):
                    if not self.is_players_piece(piece.player, possible_dst) or count_self:
                        valid_dsts.append(possible_dst)

                    if self.get_piece(possible_dst):
                        break

        return valid_dsts


    def is_players_piece(self, player, coords):
        return self.get_piece(coords) and self.get_piece(coords).player == player


    def is_opponent_piece(self, dst):
        """
        """
        dst_piece = self.get_piece(dst)
        if dst_piece != "" and dst_piece.player != self.current_player:
            return True
        return False

    def in_bounds(self, dst):
        return 0 <= dst[0] < 5 and 0 <= dst[1] < 5


    def place_piece(self, piece, coords):
        """ Places Piece at position coords on this Board's grid
        """
        piece.coords = coords

        if type(piece) == King:
            if piece.player == "UPPER":
                self.king_UPPER = piece
            else:
                self.king_lower = piece

        if piece.player == "UPPER":
            self.pieces_UPPER.append(piece)
        else:
            self.pieces_lower.append(piece)

        for blockable_piece in self.blockable_pieces:
            self.update_heatmap(blockable_piece.coords, -1)

        self.grid[coords[0]][coords[1]] = piece
        self.update_heatmap(coords, 1)

        for blockable_piece in self.blockable_pieces:
            self.update_heatmap(blockable_piece.coords, 1)

        if piece.blockable:
            self.blockable_pieces.append(piece)


    def get_piece(self, coords):
        """ Returns Piece if it exists at these coords
        """
        return self.grid[coords[0]][coords[1]]


    def remove_piece(self, coords):
        """ Removes piece from grid if it exists at these coords
        """
        piece = self.get_piece(coords)

        self.update_heatmap(coords, -1)
        self.grid[coords[0]][coords[1]] = ""

        if piece.blockable:
            self.blockable_pieces.remove(piece)

        if piece.player == "UPPER":
            self.pieces_UPPER.remove(piece)
        else:
            self.pieces_lower.remove(piece)


    def move_piece(self, src, dst, enforce_player=True):
        """ Move a piece from start to destination if it is a valid move.
        """

        piece = self.get_piece(src)

        if piece.player != self.current_player and enforce_player:
            return False

        if dst in self.get_valid_dsts(src):
            if self.is_opponent_piece(dst):
                self.capture_piece(dst)
                self.remove_piece(src)
                self.place_piece(piece, dst)

            elif not self.get_piece(dst):
                self.remove_piece(src)
                self.place_piece(piece, dst)

            else:
                return False

            return True
        else:
            return False

    def capture_piece(self, coords):
        """ adds captured piece to the list of the current player
        """
        piece = self.get_piece(coords)
        self.remove_piece(coords)

        if self.current_player == "UPPER":
            self.captures_UPPER.append(piece)
        else:
            self.captures_lower.append(piece)


    def drop_piece(self, icon, dst):
        """ Drops captured piece onto the board. Removes piece from captured pieces.
        """
        if self.get_piece(dst):
            return False

        if self.current_player == "UPPER":
            captured_pieces = self.captures_UPPER
        else:
            captured_pieces = self.captures_lower

        # TODO: Perhaps convert captured_pieces to a set for O(1) access
        icons = [p.icon for p in captured_pieces]

        drop_piece = None
        for i in range(len(icons)):
            if icon == icons[i]:
                drop_piece = captured_pieces[i]

        if not drop_piece:
            print("You have not captured that piece.")
            return False

        # Demote and convert the piece to other player
        captured_pieces.remove(drop_piece)
        drop_piece_player = "UPPER" if drop_piece.player == "lower" else "lower"
        drop_piece = type(drop_piece)(drop_piece_player, drop_piece.coords)

        # If the piece is a Pawn, then it cannot be dropped into a promotable
        if type(drop_piece) == Pawn:
            if self.can_promote(drop_piece.player, dst):
                return False

            # checkmate condition here
            board_copy = board.copy_board()
            board_copy.place_piece(drop_piece, dst)
            if board_copy.is_checkmated("UPPER" if drop_piece.player == "lower" else "lower"):
                return False

            # two unpromoted pawns in same column condition here
            pieces = self.pieces_UPPER if drop_piece.player == "UPPER" else self.pieces_lower
            for piece in pieces:
                if type(piece) == Pawn and dst[0] == piece.coords[0]:
                    return False

        self.place_piece(drop_piece, dst)
        return True


    def can_promote(self, player, coords):
        """ Check if the piece is eligible for promotion based on its position
        """
        if player == "UPPER":
            return coords[1] == 0
        else:
            return coords[1] == 4


    def switch_current_player(self):
        if self.current_player == "UPPER":
            self.current_player = "lower"
        else:
            self.current_player = "UPPER"


    def update_heatmap(self, coords, diff):
        """ Updates the players heatmap upon placing the peace
        """
        piece = self.get_piece(coords)

        if piece.player == "UPPER":
            curr_heatmap = self.heatmap_UPPER
        else:
            curr_heatmap = self.heatmap_lower

        for dst in self.get_valid_dsts(coords, True):
            curr_heatmap[dst[0]][dst[1]] += diff

    def is_checked(self, player):
        """ Returns whether or not player is in check.
        """
        if player == "UPPER":
            other_heatmap = self.heatmap_lower
            king_coords = self.king_UPPER.coords
        else:
            other_heatmap = self.heatmap_UPPER
            king_coords = self.king_lower.coords

        return other_heatmap[king_coords[0]][king_coords[1]] > 0

    def get_uncheck_moves(self, player):
        """ If you are in check, returns the available moves to get you out of check.
        """
        uncheck_moves = {}

        pieces = self.pieces_UPPER if player == "UPPER" else self.pieces_lower

        # Iterate through all of your own pieces
        for piece in pieces:
            for dst in self.get_valid_dsts(piece.coords):
                board_copy = self.copy_board()
                board_copy.move_piece(piece.coords, dst)
                if not board_copy.is_checked(player):
                    if piece.icon in uncheck_moves:
                        uncheck_moves[piece.icon].append(coords_to_pos(dst))
                    else:
                        uncheck_moves[piece.icon] = [coords_to_pos(dst)]

        return uncheck_moves

    def is_checkmated(self, player):
        """ Returns whether or not player is checkmated.
        """
        if not self.is_checked(player):
            return False

        return self.get_uncheck_moves(player) == []


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', nargs=1, dest="filename", required=False, help='runs MiniShogi in filemode.')
    args = parser.parse_args()
    if args.filename:
        board = Board(args.filename[0])
    else:
        board = Board("")

    print(stringify_board(board.grid))

    while not board.game_over:
        # os.system('clear')
        # print("Heatmap UPPER: ")
        # print(stringify_board(board.heatmap_UPPER))
        # print(" ")
        # print("Heatmap lower: ")
        # print(stringify_board(board.heatmap_lower))

        print("Captures UPPER: " + " ".join([piece.icon for piece in board.captures_UPPER]))
        print("Captures lower: " + " ".join([piece.icon for piece in board.captures_lower]))

        if board.is_checked("UPPER"):
            print("UPPER player is in check!")
            print(board.get_uncheck_moves("UPPER"))

        if board.is_checked("lower"):
            print("lower player is in check!")
            print(board.get_uncheck_moves("lower"))

        if board.is_checkmated("UPPER"):
            print("UPPER player is checkmated GAME OVER.")
            game_over = True

        if board.is_checkmated("lower"):
            print("lower player is checkmated. GAME OVER.")
            game_over = True

        print(" ")
        user_input = input(board.current_player + "> ")

        try:
            board.execute_input(user_input)
            print(stringify_board(board.grid))

        except Exception as e:
            print(traceback.format_exc())
            print("Invalid command.")