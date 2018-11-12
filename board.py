from utils import input_to_coords, input_to_commands, stringify_board
from utils import add_coords, coords_to_pos, pos_to_coords, input_to_drop
from utils import parse_test_case, get_moves_from_dict, get_drops_from_dict, BOARD_SIZE
from pieces import Piece, King, GoldGeneral, SilverGeneral, Bishop, Rook, Pawn
import copy


class Player:

    def __init__(self, name):
        self.name = name
        self.heatmap = [[0]*BOARD_SIZE for i in range(BOARD_SIZE)]
        self.king = None
        self.is_promoted = False
        self.pieces = []
        self.captures = []
        self.num_moves = 0

    def copy(self, piece_to_copy):
        """ Returns a (deep) copy of the player.
        """
        new_player = Player(self.name)
        new_player.heatmap = copy.deepcopy(self.heatmap)
        new_player.king = piece_to_copy[self.king]
        new_player.pieces = [piece_to_copy[p] for p in self.pieces]
        new_player.captures = [piece_to_copy[cp] for cp in self.captures]

        return new_player


class Board:

    PIECE_TYPES = [King, GoldGeneral, SilverGeneral, Bishop, Rook]

    def __init__(self, init=True):
        self.grid = [[""]*BOARD_SIZE for i in range(BOARD_SIZE)]
        self.blockable_pieces = []
        self.players = {"lower" : Player("lower"), "UPPER": Player("UPPER")}
        self.current_player = self.players["lower"]

        if init:
            self.init_grid()
    
    @staticmethod
    def from_file(filename):
        board = Board(init=False)
        file_commands = board.init_grid_filemode(filename)
        return board, file_commands

    def init_grid(self):
        """ Populates pieces of initial (default) MiniShogi board state.
        """

        max_row = BOARD_SIZE - 1

        for i in range(len(Board.PIECE_TYPES)):

            piece_UPPER = Board.PIECE_TYPES[i]("UPPER", (max_row - i, max_row))
            piece_lower = Board.PIECE_TYPES[i]("lower", (i, 0))

            self.place_piece("UPPER", piece_UPPER, piece_UPPER.coords)
            self.place_piece("lower", piece_lower, piece_lower.coords)

        self.place_piece("UPPER", Pawn("UPPER", (max_row, max_row - 1)), (max_row, max_row - 1))
        self.place_piece("lower", Pawn("lower", (0, 1)), (0, 1))

    def init_grid_filemode(self, filename):
        """ Initializes grid from file config as opposed to default config.
        """
        board_metadata = parse_test_case(filename)

        for piece_dict in board_metadata["initialPieces"]:
            icon, coords = piece_dict["piece"], pos_to_coords(piece_dict["position"])
            piece = Piece.from_icon(icon, coords)
            self.place_piece(piece.player_name, piece, coords)

        self.players["UPPER"].captures = [Piece.from_icon(i) for i in board_metadata["upperCaptures"]]
        self.players["lower"].captures = [Piece.from_icon(i) for i in board_metadata["lowerCaptures"]]
        file_commands = board_metadata["moves"]

        return file_commands

    def copy(self):
        """ Returns a new board object that is a copy of the current instance (self)
        """
        all_pieces = self.players["UPPER"].pieces + self.players["lower"].pieces
        all_captures = self.players["UPPER"].captures + self.players["lower"].captures
        piece_to_copy = {piece : piece.copy() for piece in all_pieces + all_captures}
        piece_to_copy[""] = ""

        new_board = Board(init=False)

        new_board.grid = self.copy_grid(self.grid, piece_to_copy)
        new_board.players = self.copy_players(piece_to_copy)
        new_board.blockable_pieces = [piece_to_copy[bp] for bp in self.blockable_pieces]
        new_board.current_player = new_board.players[self.current_player.name]

        return new_board

    def copy_grid(self, grid, piece_to_copy):
        new_grid = [[""]*BOARD_SIZE for i in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                new_grid[i][j] = piece_to_copy[grid[i][j]]
        return new_grid

    def copy_players(self, piece_to_copy):
        new_players = {}
        for name in self.players:
            new_players[name] = self.players[name].copy(piece_to_copy)
        return new_players

    def try_move_piece(self, piece, dst):
        """ Returns a copy of the board after specified move command.
        """
        board_copy = self.copy()
        piece_copy = board_copy.get_piece(piece.coords)
        board_copy.move_piece(piece_copy, dst)
        
        return board_copy

    def try_drop_piece(self, player, piece, dst):
        """ Returns a copy of the board after specified drop command.
        """
        board_copy = self.copy()
        piece_copy = self.get_copy_from_captures(piece, self.current_player.captures)
        board_copy.drop_piece(board_copy.players[player.name], piece_copy, dst)

        return board_copy

    def can_promote(self, piece, src, dst):
        """ Check if the piece is eligible for promotion based on its position
        """
        if type(piece) == King or type(piece) == GoldGeneral or piece.is_promoted:
            return False
        elif piece.player_name == "UPPER":
            return dst[1] == 0 or src[1] == 0
        else:
            return dst[1] == 4 or src[1] == 4

    def get_valid_dsts(self, piece, count_own_pieces=False):
        """ returns all valid destinations a piece can move to.
        """

        valid_dsts = []

        player = self.players[piece.player_name]

        for move in piece.unblockable_moves:
            possible_dst = add_coords(player, move, piece.coords)
            if self.is_valid_dst(piece, possible_dst, count_own_pieces):
                valid_dsts.append(possible_dst)

        for moves_set in piece.blockable_moves_sets:
            for move in moves_set:
                possible_dst = add_coords(player, move, piece.coords)

                if self.is_valid_dst(piece, possible_dst, count_own_pieces):
                    valid_dsts.append(possible_dst)

                if self.in_bounds(possible_dst) and self.get_piece(possible_dst):
                    break

        return valid_dsts

    def is_valid_dst(self, piece, dst, count_own_pieces):
        other_player_name = self.get_other_player_name(piece.player_name)
        
        if self.in_bounds(dst):
            if not self.is_players_piece(piece.player_name, dst) or count_own_pieces:
                if type(piece) != King or self.get_heatmap_val(other_player_name, dst) == 0:
                    return True
        
        return False
    
    def get_other_player(self, player):
        if player.name == "UPPER":
            return self.players["lower"]
        return self.players["UPPER"]

    def get_other_player_name(self, player_name):
        return "UPPER" if player_name == "lower" else "lower"

    def is_players_piece(self, player_name, coords):
        return self.get_piece(coords) and self.get_piece(coords).player_name == player_name

    def is_opponent_piece(self, piece):
        if piece != "" and piece.player_name != self.current_player.name:
            return True
        return False
    
    def in_bounds(self, dst):
        return 0 <= dst[0] < BOARD_SIZE and 0 <= dst[1] < BOARD_SIZE

    def place_piece(self, player_name, piece, coords):
        piece.coords = coords

        for blockable_piece in self.blockable_pieces:
            self.update_heatmap(blockable_piece, -1)

        self.grid[coords[0]][coords[1]] = piece
        self.update_heatmap(piece, 1)

        for blockable_piece in self.blockable_pieces:
            self.update_heatmap(blockable_piece, 1)

        player = self.players[player_name]

        if type(piece) == King:
            player.king = piece

        player.pieces.append(piece)

        if piece.blockable:
            self.blockable_pieces.append(piece)

    def get_piece(self, coords):
        return self.grid[coords[0]][coords[1]]

    def move_piece(self, piece, dst, enforce_player=True):
        """ Move a piece to dst if it is a valid move.
        """

        if piece.player_name != self.current_player.name and enforce_player:
            return False

        if dst in self.get_valid_dsts(piece):
            if self.is_opponent_piece(self.get_piece(dst)):
                self.capture_piece(self.get_piece(dst))
                self.remove_piece(piece)
                self.place_piece(self.current_player.name, piece, dst)
                return True

            elif not self.get_piece(dst):
                self.remove_piece(piece)
                self.place_piece(self.current_player.name, piece, dst)
                return True
        
        return False
    
    def remove_piece(self, piece):
        if piece.blockable:
            self.blockable_pieces.remove(piece)

        for blockable_piece in self.blockable_pieces:
            self.update_heatmap(blockable_piece, -1)

        self.update_heatmap(piece, -1)
        self.grid[piece.coords[0]][piece.coords[1]] = ""

        for blockable_piece in self.blockable_pieces:
            self.update_heatmap(blockable_piece, 1)

        self.players[piece.player_name].pieces.remove(piece)

    def capture_piece(self, piece):
        """ adds captured piece to the list of the current player
        """
        self.remove_piece(piece)
        capture_player = self.players[self.get_other_player_name(piece.player_name)]
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
            return False

        if type(piece) == Pawn and not self.can_drop_pawn(player, piece, dst):
            return False

        self.place_piece(self.current_player.name, piece, dst)
        captured_pieces.remove(piece)
        return True
    
    def can_drop_pawn(self, player, piece, dst):
        if self.can_promote(piece, piece.coords, dst):
            return False

        board_copy = self.copy()
        captures_copy = board_copy.current_player.captures
        piece_copy = self.get_copy_from_captures(piece, captures_copy)

        board_copy.place_piece(piece.player_name, piece_copy, dst)
        captures_copy.remove(piece_copy)

        other_player = board_copy.get_other_player(player)
        if board_copy.is_checkmated(other_player, False):
            return False

        for p in player.pieces:
            if type(p) == Pawn and dst[0] == p.coords[0]:
                return False
        
        return True
    
    def get_copy_from_captures(self, piece, captures):
        """ Returns the corresponding copied piece from captures.
        """
        for captured_piece in captures:
            if captured_piece == piece:
                return captured_piece

    def update_heatmap(self, piece, diff):
        """ 
        Updates the player's heatmap upon placing the piece.

        A heatmap is a 2-D grid of ints where each cell's value
        represents how many of the players' pieces can reach
        this cell.
        """
        curr_heatmap = self.players[piece.player_name].heatmap

        for dst in self.get_valid_dsts(piece, True):
            curr_heatmap[dst[0]][dst[1]] += diff
    
    def get_heatmap_val(self, player_name, coords):
        return self.players[player_name].heatmap[coords[0]][coords[1]]

    def is_checked(self, player):
        """ Returns whether or not player is in check by other_player.
        """
        other_player = self.players[self.get_other_player_name(player.name)]
        other_heatmap = other_player.heatmap
        king_coords = player.king.coords

        return other_heatmap[king_coords[0]][king_coords[1]] > 0
    
    def is_checkmated(self, player, check_drops=True):
        """ Returns whether or not player is checkmated.
        """
        if not self.is_checked(player):
            return False

        if check_drops:
            return not self.get_uncheck_moves(player) and not self.get_uncheck_drops(player)
        else:
            return not self.get_uncheck_moves(player)

    def get_uncheck_moves(self, player):
        """ Returns available moves to get  out of check.
        """
        uncheck_moves = {}
        pieces = player.pieces

        for piece in pieces:
            for dst in self.get_valid_dsts(piece):
                board_copy = self.try_move_piece(piece, dst)

                if not board_copy.is_checked(board_copy.players[player.name]):
                    if (piece.icon, piece.coords) not in uncheck_moves:
                        uncheck_moves[(piece.icon, piece.coords)] = []

                    uncheck_moves[(piece.icon, piece.coords)].append(coords_to_pos(dst))

        return uncheck_moves
    
    def get_uncheck_drops(self, player):
        """ Returns available drops to get out of check.
        """
        uncheck_drops = {}

        for piece in player.captures:
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    dst = (i, j)
                    board_copy = self.try_drop_piece(player, piece, dst)

                    if not board_copy.is_checked(board_copy.players[player.name]):
                        if piece.icon not in uncheck_drops:
                            uncheck_drops[piece.icon] = []
                            
                        uncheck_drops[piece.icon].append(coords_to_pos(dst))
        
        return uncheck_drops

    def switch_current_player(self):
        if self.current_player.name == "UPPER":
            self.current_player = self.players["lower"]
        else:
            self.current_player = self.players["UPPER"]
    
    def __str__(self):
        return stringify_board(self.grid)