from utils import input_to_coords, input_to_commands, stringify_board
from utils import add_coords, coords_to_pos, pos_to_coord, input_to_drop, parse_test_case
from utils import get_moves_from_dict, get_drops_from_dict
import os, sys
import time
import traceback
import ast
import copy
import argparse

BOARD_SIZE = 5

class Player:

    def __init__(self, name):
        """
        """
        self.name = name
        self.heatmap = [[0]*BOARD_SIZE for i in range(BOARD_SIZE)]
        self.king = None
        self.is_promoted = False
        self.pieces = []
        self.captures = []
        self.num_moves = 0

    def copy(self, piece_to_copy):
        """ Returns a (deep) copy of the player
        """
        new_player = Player(self.name)
        new_player.heatmap = copy.deepcopy(self.heatmap)
        new_player.king = piece_to_copy[self.king]
        new_player.pieces = [piece_to_copy[p] for p in self.pieces]
        new_player.captures = [piece_to_copy[cp] for cp in self.captures]

        return new_player


class Piece:

    num_pieces = 0

    def __init__(self, player_name, coords, icon, blockable, copy):
        """ Initializes piece.
        """
        self.player_name = player_name
        if not copy:
            self.id = Piece.num_pieces
            Piece.num_pieces += 1
        self.coords = coords
        self._icon = icon
        self.is_promoted = False
        self.blockable = blockable

    @property
    def icon(self):
        ret_icon = self._icon
        if self.player_name == "lower":
            ret_icon = self._icon.lower()
        if self.is_promoted:
            ret_icon = "+" + ret_icon
        return ret_icon

    def copy(self):
        """ Returns a copy of the piece.
        """
        piece_type = type(self)
        new_piece = piece_type(self.player_name, self.coords, True)
        new_piece.id = self.id
        return new_piece

    def demote(self):
        """ Demotes piece of promoted, otherwise does nothing.
        """
        self.is_promoted = False
        self.blockable_moves_sets = type(self).blockable_moves_sets
        self.unblockable_moves = type(self).unblockable_moves

    def __eq__(self, other):
        """ Equality comparator for pieces.
        """
        return type(self) == type(other) and self.id == other.id

    def __hash__(self):
        """ Hash function for pieces
        """
        return hash(self.id)


class King(Piece):

    blockable_moves_sets = []
    unblockable_moves = [(-1, 1), (0, 1), 
                         (1, 1), (1, 0), 
                         (1, -1), (0, -1), 
                         (-1, -1), (-1, 0)]

    def __init__(self, player, coords, copy=False):
        super().__init__(player, coords, "K", False, copy)

    def promote(self):
        return False


class GoldGeneral(Piece):

    blockable_moves_sets = []
    unblockable_moves = [(-1, 1), (0, 1), 
                         (1, 1), (1, 0), 
                         (0, -1), (-1, 0)]

    def __init__(self, player, coords, copy=False):
        super().__init__(player, coords, "G", False, copy)

    def promote(self):
        return False


class SilverGeneral(Piece):

    blockable_moves_sets = []
    unblockable_moves = [(-1, 1), (0, 1), 
                         (1, 1), (1, -1), 
                         (-1, -1)]

    def __init__(self, player, coords, copy=False):
        super().__init__(player, coords, "S", False, copy)

    def promote(self):
        self.is_promoted = True
        self.unblockable_moves = GoldGeneral.unblockable_moves
        return True


class Bishop(Piece):

    up_right_moves = [(1, 1), (2, 2), (3, 3), (4, 4)]
    down_right_moves = [(1, -1), (2, -2), (3, -3), (4, -4)]
    down_left_moves = [(-1, -1), (-2, -2), (-3, -3), (-4, -4)]
    up_left_moves = [(-1, 1), (-2, 2), (-3, 3), (-4, 4)]

    blockable_moves_sets = [up_right_moves, down_left_moves, down_right_moves, up_left_moves]
    unblockable_moves = []

    def __init__(self, player, coords, copy=False):
        super().__init__(player, coords, "B", True, copy)

    def promote(self):
        self.is_promoted = True
        self.unblockable_moves.extend(King.unblockable_moves)
        return True


class Rook(Piece):

    up_moves = [(0, 1), (0, 2), (0, 3), (0, 4)]
    right_moves = [(1, 0), (2, 0), (3, 0), (4, 0)]
    down_moves = [(0, -1), (0, -2), (0, -3), (0, -4)]
    left_moves = [(-1, 0), (-2, 0), (-3, 0), (-4, 0)]

    unblockable_moves = []
    blockable_moves_sets = [up_moves, right_moves, down_moves, left_moves]

    def __init__(self, player, coords, copy=False):
        super().__init__(player, coords, "R", True, copy)

    def promote(self):
        self.is_promoted = True
        self.unblockable_moves.extend(King.unblockable_moves)
        return True


class Pawn(Piece):

    unblockable_moves = [(0, 1)]
    blockable_moves_sets = []

    def __init__(self, player, coords, copy=False):
        super().__init__(player, coords, "P", False, copy)

    def promote(self):
        self.is_promoted = True
        self.unblockable_moves = GoldGeneral.unblockable_moves
        return True


class Board:

    def __init__(self, filename, copy=False):
        """ Initializes board.
        """
        self.BOARD_SIZE = 5
        self.grid = [[""]*self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        self.blockable_pieces = []
        self.players = {"lower" : Player("lower"), "UPPER": Player("UPPER")}
        self.current_player = self.players["lower"]
        self.game_over = False
        self.file_over = False
        self.last_command = ""
        self.file_index = 0

        if filename:
            self.init_grid_filemode(filename)
        elif not copy:
            self.init_grid()

    def init_grid(self):
        """ Populates pieces of initial board state.
        """

        pieces = [King, GoldGeneral, SilverGeneral, Bishop, Rook]

        for i in range(self.BOARD_SIZE):

            piece_UPPER = pieces[i]("UPPER", (4 - i, 4))
            piece_lower = pieces[i]("lower", (i, 0))

            self.place_piece(self.players["UPPER"], piece_UPPER, piece_UPPER.coords)
            self.place_piece(self.players["lower"], piece_lower, piece_lower.coords)

        self.place_piece(self.players["UPPER"], Pawn("UPPER", (4, 3)), (4, 3))
        self.place_piece(self.players["lower"], Pawn("lower", (0, 1)), (0, 1))

    def init_grid_filemode(self, filename):
        """ Initializes grid from file config as opposed to default config.
        """
        icon_to_piece = {'k': King, 'g': GoldGeneral, 's': SilverGeneral, 
                         'b': Bishop, 'r': Rook, 'p': Pawn}
        filemode_dict = parse_test_case(filename)
        for piece_dict in filemode_dict["initialPieces"]:
            icon, pos = piece_dict["piece"], pos_to_coord(piece_dict["position"])
            stripped_icon = icon.strip("+")
            player_name = "UPPER" if stripped_icon.isupper() else "lower"
            stripped_icon = stripped_icon.lower()
            piece = icon_to_piece[stripped_icon](player_name, pos)
            if "+" in icon:
                piece.promote()
            self.place_piece(self.players[player_name], piece, pos)

        self.players["UPPER"].captures = [icon_to_piece[i.lower()]("UPPER", (-1, -1)) for i in filemode_dict["upperCaptures"]]
        self.players["lower"].captures = [icon_to_piece[i.lower()]("lower", (-1, -1)) for i in filemode_dict["lowerCaptures"]]
        self.filemode_commands = filemode_dict["moves"]
    
    def next_file_command(self):
        """ returns next file command
        """
        if self.file_index >= len(self.filemode_commands):
            self.file_over = True
            return ""

        command = self.filemode_commands[self.file_index]
        self.file_index += 1
        return command

    def copy(self):
        """ Returns a new board object that is a copy of the current instance (self)
        """
        all_pieces = self.players["UPPER"].pieces + self.players["lower"].pieces
        all_captures = self.players["UPPER"].captures + self.players["lower"].captures
        piece_to_copy = {piece : piece.copy() for piece in all_pieces + all_captures}
        piece_to_copy[""] = ""

        new_board = Board("", True)

        new_board.grid = self.copy_grid(self.grid, piece_to_copy)
        new_board.BOARD_SIZE = self.BOARD_SIZE
        new_board.players = self.copy_players(piece_to_copy)
        new_board.blockable_pieces = [piece_to_copy[bp] for bp in self.blockable_pieces]
        new_board.current_player = new_board.players[self.current_player.name]

        return new_board

    def copy_grid(self, grid, piece_to_copy):
        new_grid = [[""]*self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                new_grid[i][j] = piece_to_copy[grid[i][j]]
        return new_grid

    def copy_players(self, piece_to_copy):
        new_players = {}
        for name in self.players:
            new_players[name] = self.players[name].copy(piece_to_copy)
        return new_players

    def execute_input(self, user_input):
        if not self.file_over:
            self.last_command = user_input
        command, promote = input_to_commands(user_input)

        # Execute move command
        if command == "move":
            return self.execute_move(user_input, promote)

        elif command == "drop":
            return self.execute_drop(user_input)

        return False

    def execute_move(self, user_input, promote):
        src, dst = input_to_coords(user_input)
        piece = self.get_piece(src)

        if promote and self.can_promote(piece, piece.coords, dst):
            if self.move_piece(piece, dst):
                return piece.promote()

        elif type(piece) == Pawn and self.can_promote(piece, piece.coords, dst):
            if self.move_piece(piece, dst):
                return piece.promote()

        elif not promote:
            return self.move_piece(piece, dst)

        return False

    def can_promote(self, piece, src, dst):
        """ Check if the piece is eligible for promotion based on its position
        """
        if type(piece) == King or type(piece) == GoldGeneral or piece.is_promoted:
            return False
        if piece.player_name == "UPPER":
            return dst[1] == 0 or src[1] == 0
        else:
            return dst[1] == 4 or src[1] == 4

    def execute_drop(self, user_input):
        icon, dst = input_to_drop(user_input)
        for piece in self.current_player.captures:
            if piece.icon.lower() == icon.lower():
                return self.drop_piece(self.current_player, piece, pos_to_coord(dst))
        return False

    def get_valid_dsts(self, piece, count_self=False):
        """ returns all valid destinations a piece can move to.
        """

        valid_dsts = []

        for move in piece.unblockable_moves:
            possible_dst = add_coords(self.players[piece.player_name], move, piece.coords)
            if self.in_bounds(possible_dst):
                if not self.is_players_piece(self.players[piece.player_name], possible_dst) or count_self:
                    # Can't move King into check
                    opp_heatmap = self.get_other_player(self.current_player).heatmap
                    if type(piece) == King and opp_heatmap[possible_dst[0]][possible_dst[1]] > 0:
                        pass
                    else:
                        valid_dsts.append(possible_dst)

        for moves_set in piece.blockable_moves_sets:
            for move in moves_set:
                possible_dst = add_coords(self.current_player, move, piece.coords)

                if self.in_bounds(possible_dst):
                    if not self.is_players_piece(self.players[piece.player_name], possible_dst) or count_self:
                        valid_dsts.append(possible_dst)

                    if self.get_piece(possible_dst):
                        break

        return valid_dsts

    def get_other_player(self, player):
        """ Returns the player who is not player.
        """
        return self.players["UPPER"] if player.name == "lower" else self.players["lower"]

    def is_players_piece(self, player, coords):
        return self.get_piece(coords) and self.get_piece(coords).player_name == player.name

    def is_opponent_piece(self, piece):
        """
        """
        if piece != "" and piece.player_name != self.current_player.name:
            return True
        return False

    def in_bounds(self, dst):
        return 0 <= dst[0] < 5 and 0 <= dst[1] < 5

    def place_piece(self, player, piece, coords):
        """ Places Piece at position coords on this Board's grid
        """
        piece.coords = coords

        if type(piece) == King:
            player.king = piece

        player.pieces.append(piece)

        for blockable_piece in self.blockable_pieces:
            self.update_heatmap(blockable_piece, -1)

        self.grid[coords[0]][coords[1]] = piece
        self.update_heatmap(piece, 1)

        for blockable_piece in self.blockable_pieces:
            self.update_heatmap(blockable_piece, 1)

        if piece.blockable:
            self.blockable_pieces.append(piece)

    def get_piece(self, coords):
        """ Returns Piece if it exists at these coords
        """
        return self.grid[coords[0]][coords[1]]

    def remove_piece(self, piece):
        """ Removes piece from grid if it exists at these coords
        """
        if piece.blockable:
            self.blockable_pieces.remove(piece)

        for blockable_piece in self.blockable_pieces:
            self.update_heatmap(blockable_piece, -1)

        self.update_heatmap(piece, -1)
        self.grid[piece.coords[0]][piece.coords[1]] = ""

        for blockable_piece in self.blockable_pieces:
            self.update_heatmap(blockable_piece, 1)

        self.players[piece.player_name].pieces.remove(piece)

    def move_piece(self, piece, dst, enforce_player=True):
        """ Move a piece from start to destination if it is a valid move.
        """

        if piece.player_name != self.current_player.name and enforce_player:
            return False

        self.get_valid_dsts(piece)

        if dst in self.get_valid_dsts(piece):
            if self.is_opponent_piece(self.get_piece(dst)):
                self.capture_piece(self.get_piece(dst))
                self.remove_piece(piece)
                self.place_piece(self.current_player, piece, dst)

            elif not self.get_piece(dst):
                self.remove_piece(piece)
                self.place_piece(self.current_player, piece, dst)

            else:
                return False

            return True
        else:
            return False

    def capture_piece(self, piece):
        """ adds captured piece to the list of the current player
        """
        self.remove_piece(piece)
        capture_player = self.get_other_player(self.players[piece.player_name])
        piece.demote()
        piece.player_name = capture_player.name
        capture_player.captures.append(piece)

    def drop_piece(self, player, piece, dst):
        """ Drops captured piece onto the board. Removes piece from captured pieces.
        """
        if self.get_piece(dst):
            return False

        captured_pieces = player.captures

        if not piece:
            print("You have not captured that piece.")
            return False

        # If the piece is a Pawn, then it cannot be dropped into a promotable
        if type(piece) == Pawn:
            if self.can_promote(piece, piece.coords, dst):
                return False

            # checkmate condition here
            board_copy = board.copy()
            for captured_piece in board_copy.current_player.captures:
                if captured_piece == piece:
                    copy_piece = piece

            board_copy.place_piece(board_copy.current_player, copy_piece, dst)
            board_copy.current_player.captures.remove(copy_piece)
            other_player = board_copy.get_other_player(board_copy.players[piece.player_name])
            if board_copy.is_checkmated(other_player, False):
                return False

            # two unpromoted pawns in same column condition here
            for p in player.pieces:
                if type(p) == Pawn and dst[0] == p.coords[0]:
                    return False

        self.place_piece(self.current_player, piece, dst)
        captured_pieces.remove(piece)
        return True

    def switch_current_player(self):
        if self.current_player.name == "UPPER":
            self.current_player = self.players["lower"]
        else:
            self.current_player = self.players["UPPER"]

    def update_heatmap(self, piece, diff):
        """ Updates the players heatmap upon placing the peace
        """
        curr_heatmap = self.players[piece.player_name].heatmap

        for dst in self.get_valid_dsts(piece, True):
            curr_heatmap[dst[0]][dst[1]] += diff

    def is_checked(self, player):
        """ Returns whether or not player is in check by other_player.
        """
        other_player = self.get_other_player(player)
        other_heatmap = other_player.heatmap
        king_coords = player.king.coords

        return other_heatmap[king_coords[0]][king_coords[1]] > 0

    def get_uncheck_moves(self, player):
        """ If you are in check, returns the available moves to get you out of check.
        """
        uncheck_moves = {}
        pieces = player.pieces

        # Iterate through all of your own pieces
        for piece in pieces:
            for dst in self.get_valid_dsts(piece):
                board_copy = self.copy()
                piece_copy = board_copy.get_piece(piece.coords)
                board_copy.move_piece(piece_copy, dst)
                if not board_copy.is_checked(board_copy.players[piece.player_name]):
                    if (piece.icon, piece.coords) in uncheck_moves:
                        uncheck_moves[(piece.icon, piece.coords)].append(coords_to_pos(dst))
                    else:
                        uncheck_moves[(piece.icon, piece.coords)] = [coords_to_pos(dst)]

        return uncheck_moves
    
    def get_uncheck_drops(self, player):
        """ If you are in check, returns the available drops to get you out of check.
        """
        uncheck_drops = {}

        for piece in player.captures:
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    board_copy = self.copy()
                    for captured_piece in board_copy.players[player.name].captures:
                        if captured_piece == piece:
                            piece_copy = captured_piece
                    board_copy.drop_piece(board_copy.players[player.name], piece_copy, (i, j))
                    if not board_copy.is_checked(board_copy.players[player.name]):
                        if piece.icon in uncheck_drops:
                            uncheck_drops[piece.icon].append(coords_to_pos((i, j)))
                        else:
                            uncheck_drops[piece.icon] = [coords_to_pos((i, j))]
        
        return uncheck_drops

    def is_checkmated(self, player, check_drops=True):
        """ Returns whether or not player is checkmated.
        """
        if not self.is_checked(player):
            return False

        if check_drops:
            return not self.get_uncheck_moves(player) and not self.get_uncheck_drops(player)
        else:
            return not self.get_uncheck_moves(player)
    
    def print_metadata(self):
        print("Captures UPPER: " + " ".join([piece.icon for piece in self.players["UPPER"].captures]))
        print("Captures lower: " + " ".join([piece.icon for piece in self.players["lower"].captures]))
        print("")
        

        if self.is_checkmated(self.players["UPPER"]):
            board.winner = "lower"
            board.winner_reason = "Checkmate."
            board.game_over = True

        if self.is_checkmated(self.players["lower"]):
            board.winner = "UPPER"
            board.winner_reason = "Checkmate."
            board.game_over = True

        if not self.game_over and self.current_player.num_moves > 199:
            print("Tie game.  Too many moves.")
            board.winner = ""
            board.winner_reason = ""
            board.game_over = True

        if not self.game_over and self.is_checked(self.players["UPPER"]):
            print("UPPER player is in check!")
            print("Available moves:")
            moves = get_moves_from_dict(self.get_uncheck_moves(self.players["UPPER"]))
            drops = get_drops_from_dict(self.get_uncheck_drops(self.players["UPPER"]))
            for drop in sorted(drops):
                print(drop)
            
            for move in sorted(moves):
                print(move)

        if not self.game_over and self.is_checked(self.players["lower"]):
            print("lower player is in check!")
            print("Available moves:")
            moves = get_moves_from_dict(self.get_uncheck_moves(self.players["lower"]))
            drops = get_drops_from_dict(self.get_uncheck_drops(self.players["lower"]))   
            for drop in sorted(drops):
                print(drop)
            
            for move in sorted(moves):
                print(move)

        if not board.game_over:
            print(self.current_player.name + "> ", end="")

    def print_state(self):
        """ Prints state of the game.
        """
        print(self.get_other_player(self.players[self.current_player.name]).name + " player action: " + board.last_command.strip()) 
        print(stringify_board(self.grid))
        self.print_metadata()
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', nargs=1, dest="filename", required=False, help='runs MiniShogi in filemode.')
    args = parser.parse_args()

    if args.filename:
        filemode = True
        board = Board(args.filename[0])
        get_input = board.next_file_command
    else:
        filemode = False
        board = Board("")
        get_input = input

    while not board.game_over:

        if not filemode:
            board.print_state()

        user_input = get_input()
        if board.execute_input(user_input):
            if not filemode:
                print(board.current_player.name + " player action: " + board.last_command.strip()) 
            board.switch_current_player()
            board.current_player.num_moves += 1
            if not filemode:
                print(stringify_board(board.grid))
        
        elif board.file_over:
            break

        else:
            board.switch_current_player()
            board.winner = board.current_player.name
            board.winner_reason = "Illegal move."
            board.game_over = True

    if filemode:
        board.print_state()
        if board.game_over and board.winner and board.winner_reason:
            print(board.winner + " player wins.  " + board.winner_reason)