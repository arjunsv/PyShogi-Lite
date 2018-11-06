from utils import input_to_coords, input_to_commands, stringify_board, add_coords
import os, sys
import time
import traceback


class Piece:

    def __init__(self, player, coords, blockable):
        """ Initializes piece
        """
        self.player = player
        self.blockable = blockable
        self.coords = coords

        if self.player == "lower":
            self.icon = self.icon.lower()


class King(Piece):

    def __init__(self, player, coords):
        self.icon = "K"
        super().__init__(player, coords, False)
        self.blockable_moves_sets = []
        self.unblockable_moves = [(-1, 1), (0, 1), 
                                  (1, 1), (1, 0), 
                                  (1, -1), (0, -1), 
                                  (-1, -1), (-1, 0)]

    def promote(self):
        print("King cannot be promoted.")


class GoldGeneral(Piece):

    def __init__(self, player, coords):
        self.icon = "G"
        super().__init__(player, coords, False)
        self.blockable_moves_sets = []
        self.unblockable_moves = [(-1, 1), (0, 1), 
                                  (1, 1), (1, 0), 
                                  (0, -1), (-1, 0)]

    def promote(self):
        print("Gold General cannot be promoted.")


class SilverGeneral(Piece):

    blockable_moves_sets = []
    unblockable_moves = [(-1, 1), (0, 1), 
                         (1, 1), (1, -1), 
                         (-1, -1)]

    def __init__(self, player, coords):
        self.icon = "S"
        super().__init__(player, coords, False)

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
        self.icon = "B"
        super().__init__(player, coords, True)

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
        super().__init__(player, coords, True)

    def promote(self):
        self.icon = "+" + self.icon
        self.unblockable_moves.extend(King.unblockable_moves)


class Pawn(Piece):

    unblockable_moves = [(0, 1)]
    blockable_moves_sets = []

    def __init__(self, player, coords):
        self.icon = "P"
        super().__init__(player, coords, False)

    def promote(self):
        self.icon = "+" + self.icon
        self.unblockable_moves = GoldGeneral.unblockable_moves


class Board:

    def __init__(self):
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
        self.init_grid()


    def init_grid(self):
        """ Populates pieces of initial board state.
        """
        pieces = [King, GoldGeneral, SilverGeneral, Bishop, Rook]

        for i in range(self.BOARD_SIZE):

            piece_UPPER = pieces[i]("UPPER", (4 - i, 4))
            piece_lower = pieces[i]("lower", (i, 0))

            self.place_piece(piece_UPPER, piece_UPPER.coords)
            print(" ")
            self.place_piece(piece_lower, piece_lower.coords)

        self.place_piece(Pawn("UPPER", (4, 3)), (4, 3))
        self.place_piece(Pawn("lower", (0, 1)), (0, 1))


    def init_grid_filemode(self, filename):
        """ Initializes grid from file config as opposed to default config.
        """
        pass


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


    def get_valid_dsts(self, coords, count_self=False):
        """ returns all valid destinations a piece can move to.
        """

        valid_dsts = []
        piece = self.get_piece(coords)

        for move in piece.unblockable_moves:
            possible_dst = add_coords(self.current_player, move, coords)
            if self.in_bounds(possible_dst):
                if not self.is_players_piece(piece.player, possible_dst) or count_self:
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

    def capture_piece(self, coords):
        """ adds captured piece to the list of the current player
        """
        piece = self.get_piece(coords)
        self.remove_piece(coords)

        if self.current_player == "UPPER":
            self.captures_UPPER.append(piece)
        else:
            self.captures_lower.append(piece)

    def can_promote(self, coords):
        """ Check if the piece is eligible for promotion based on its position
        """
        return coords[1] == 0 or coords[1] == 4

    def switch_current_player(self):
        if self.current_player == "UPPER":
            self.current_player = "lower"
        else:
            self.current_player = "UPPER"

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

    def is_checkmated(self, player):
        """ Returns whether or not player is checkmated.
        """
        if not self.is_checked(player):
            return False

        pieces = self.pieces_UPPER if player == "UPPER" else self.pieces_lower
        for piece in pieces[:]:
            piece_coords = piece.coords
            valid_dsts = self.get_valid_dsts(piece_coords)
            for dst in valid_dsts:

                captures_before = self.captures_UPPER[:] if player == "UPPER" else self.captures_lower[:]

                self.move_piece(piece_coords, dst, False)
                self.get_piece(dst)

                captures_after = self.captures_UPPER if player == "UPPER" else self.captures_lower
                is_checked = self.is_checked(player)

                self.remove_piece(dst)
                self.place_piece(piece, piece_coords)

                if len(captures_after) > len(captures_before):
                    resurrected_piece = captures_after.pop()
                    self.place_piece(resurrected_piece, dst)

                if not is_checked:
                    return False

        return True


if __name__ == "__main__":

    board = Board()
    game_over = False
    num_moves = 0


    while not game_over:
        # os.system('clear')

        print(" ")
        print("NUM MOVES: " + str(num_moves)) 
        print(" ")
        print(stringify_board(board.grid))
        print(" ")
        # print("Heatmap UPPER: ")
        # print(stringify_board(board.heatmap_UPPER))
        # print(" ")
        # print("Heatmap lower: ")
        # print(stringify_board(board.heatmap_lower))

        if board.current_player == "UPPER":
            print("Captures UPPER: " + " ".join([piece.icon for piece in board.captures_UPPER]))
        elif board.current_player == "lower":
            print("Captures lower: " + " ".join([piece.icon for piece in board.captures_lower]))

        if board.is_checked("UPPER"):
            print("UPPER player is in check!")

        if board.is_checked("lower"):
            print("lower player is in check!")

        if board.is_checkmated("UPPER"):
            print("UPPER player is checkmated GAME OVER.")
            game_over = True

        if board.is_checkmated("lower"):
            print("lower player is checkmated. GAME OVER.")
            game_over = True

        print(" ")
        user_input = input(board.current_player + "> ")

        try:

            # Parse user input
            src, dst = input_to_coords(user_input)
            command, promote = input_to_commands(user_input)

            # Execute move command
            if command == "move":
                piece = board.get_piece(src)
                if board.move_piece(src, dst):
                    if promote == "promote" and board.can_promote(dst):
                        piece.promote()
                    board.switch_current_player()
                    num_moves += 1
                else:
                    print("Invalid move.")

            elif command == "drop":
                pass


        except Exception as e:
            print(traceback.format_exc())
            print("Invalid command.")