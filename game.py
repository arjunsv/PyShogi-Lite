from utils import input_to_coords, input_to_commands, stringify_board, add_coords
import os
import time

class Piece:

    def __init__(self, player, coords, board):
        """ Initializes piece
        """
        self.player = player
        self.coords = coords

        if self.player == "lower":
            self.icon = self.icon.lower()


    def is_valid_promote(self):
        """ Check if the piece is eligible for promotion based on its position
        """
        return self.coords[1] == 0 or self.coords[1] == 4


class King(Piece):

    icon = "K"
    moves = [(-1, 1), (0, 1), 
         (1, 1), (1, 0), 
         (1, -1), (0, -1), 
         (-1, -1), (-1, 0)]

    def promote(self):
        print("King cannot be promoted.")


class GoldGeneral(Piece):

    icon = "G"
    moves = [(-1, 1), (0, 1), 
             (1, 1), (1, 0), 
             (0, -1), (-1, 0)]

    def promote(self):
        print("Gold General cannot be promoted.")


class SilverGeneral(Piece):

    icon = "S"
    moves = [(-1, 1), (0, 1), 
             (1, 1), (1, -1), 
             (-1, -1)]

    def promote(self):
        self.icon = "+" + self.icon
        self.moves = GoldGeneral.moves


class Bishop(Piece):

    icon = "B"
    moves = [(-1, 1), (-2, 2), 
             (1, 1), (2, 2), 
             (1, -1), (2, -2), 
             (-1, -1), (-2, 2)]

    def promote(self):
        self.icon = "+" + self.icon
        self.moves.extend(King.moves)


class Rook(Piece):

    icon = "R"
    moves = [(0, 1), (0, 2), 
             (1, 0), (1, 2), 
             (0, -1), (0, -2), 
             (-1, 0), (-2, 0)]

    def promote(self):
        self.icon = "+" + self.icon
        self.moves.extend(King.moves)


class Pawn(Piece):

    icon = "P"
    moves = [(0, 1)]

    def promote(self):
        self.icon = "+" + self.icon
        self.moves = GoldGeneral.moves


class Board:

    def __init__(self):
        """ Initializes board.
        """
        self.BOARD_SIZE = 5
        self.grid = [[""]*self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        self.heatmap_UPPER = [[0]*self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        self.heatmap_lower = [[0]*self.BOARD_SIZE for i in range(self.BOARD_SIZE)]
        self.captures_UPPER = []
        self.captures_lower = []
        self.current_player = "lower"
        self.init_grid()


    def init_grid(self):
        """ Populates pieces of initial board state.
        """
        pieces = [King, GoldGeneral, SilverGeneral, Bishop, Rook]

        for i in range(self.BOARD_SIZE):
            self.place_piece(pieces[i]("UPPER", (4 - i, 4), self), (4 - i, 4))
            self.place_piece(pieces[i]("lower", (i, 0), self), (i, 0))

        self.place_piece(Pawn("UPPER", (0, 3), self), (0, 3))
        self.place_piece(Pawn("lower", (4, 1), self), (4, 1))


    def init_grid_filemode(self, filename):
        """ Initializes grid from file config as opposed to default config.
        """
        pass


    def move(self, src, dst):
        """ Move a piece from start to destination if it is a valid move.
        """

        piece = self.get_piece(src)

        if self.is_valid_move(piece, src, dst):
            if self.is_opponent_piece(dst):
                self.capture_piece(dst)

            self.remove_piece(src)
            self.place_piece(piece, dst)

            return True
        else:
            return False


    def is_valid_move(self, piece, src, dst):
        """ Determines whether a particular piece is allowed to move from src to dst
            Also takes into account player's board orientation
        """
        if piece.player != self.current_player:
            print("That is not your piece.")
            return False

        possible_dsts = [add_coords(self.current_player, move, src) for move in piece.moves]

        # print(self.position)
        # print(possible_dsts)

        if dst in possible_dsts and dst[0] < 5 and dst[1] < 5:
            return True
        return False


    def is_opponent_piece(self, dst):
        """
        """
        dst_piece = self.get_piece(dst)
        if dst_piece != "" and dst_piece.player != self.current_player:
            return True
        return False


    def place_piece(self, piece, coords):
        """ Places Piece at position coords on this Board's grid
        """
        self.update_heatmap(piece, coords)
        self.grid[coords[0]][coords[1]] = piece


    def update_heatmap(self, piece, coords, diff):
        """ Updates the players heatmap upon placing the peace
        """
        
        possible_dsts = [add_coords(piece.player, move, src) for move in piece.moves]

        if piece.player == "UPPER":
            self.heatmap_UPPER[[coords[0]][coords[1]]] += diff

        elif piece.player == "lower":
            self.heatmap_lower[][[coords[0]][coords[1]]] += diff


    def get_piece(self, coords):
        """ Returns Piece if it exists at these coords
        """
        return self.grid[coords[0]][coords[1]]


    def remove_piece(self, coords):
        """ Removes piece from grid if it exists at these coords
        """
        self.grid[coords[0]][coords[1]] = ""

    def capture_piece(self, coords):
        """ adds captured piece to the list of the current player
        """
        if self.current_player == "UPPER":
            self.captures_UPPER.append(self.get_piece(coords).icon)
        else:
            self.captures_lower.append(self.get_piece(coords).icon)

    def switch_current_player(self):
        if self.current_player == "UPPER":
            self.current_player = "lower"
        else:
            self.current_player = "UPPER"

    def is_checked(self, player):
        """ Returns whether or not player is in check.
        """
        pass


    def is_checkmated(self, player):
        """ Returns whether or not player is checkmated.
        """
        if self.is_checked(player):
            return
        return False

    # Heatmap functions
    def can_block_check(self):


class Heatmap:

    def can_block_check(self):
        pass

    def can_capture_check(self):
        pass

    def can_move_king(self):
        pass



if __name__ == "__main__":

    board = Board()
    game_over = False
    num_moves = 0


    while not game_over:
        os.system('clear')

        print(" ")
        print("NUM MOVES: " + str(num_moves)) 
        print(" ")
        print(stringify_board(board.grid))
        print(stringify_board())

        if board.current_player == "UPPER":
            print("Captures UPPER: " + " ".join(board.captures_UPPER))
        elif board.current_player == "lower":
            print("Captures lower: " + " ".join(board.captures_lower))

        print(" ")
        user_input = input(board.current_player + "> ")

        try:

            # Parse user input
            src, dst = input_to_coords(user_input)
            command, promote = input_to_commands(user_input)

            # Execute move command
            if command == "move":
                piece = board.get_piece(src)
                if board.move(src, dst):
                    board.switch_current_player()
                if promote == "promote":
                    piece.promote()

            elif command == "drop":
                pass

            num_moves += 1

        except Exception as e:
            print(e)
            print("Invalid command.")