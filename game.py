from utils import input_to_coords, input_to_commands, stringify_board
from utils import add_coords, coords_to_pos, pos_to_coords, input_to_drop
from utils import parse_test_case, get_moves_from_dict, get_drops_from_dict
from board import Board, Player
from pieces import Piece, King, GoldGeneral, SilverGeneral, Bishop, Rook, Pawn
import copy
import argparse
import sys


class Game:

    def __init__(self, filename=None):
        if filename:
            self.file_index = 0
            self.is_filemode = True
            self.board, self.file_commands = Board.from_file(args.filename[0])
        else:
            self.is_filemode = False
            self.board = Board()
        
        self.winner = ""
        self.winner_reason = ""
        self.last_command = ""
        self.game_over = False
        self.file_over = False

    def play(self):
        """ Plays a game of Shogi until a player loses.
        """
        while not self.game_over and not self.file_over:
            if not self.is_filemode:
                self.print_state()

            user_input = self.get_input()
            if self.execute_input(user_input):
                self.board.switch_current_player()
                self.board.current_player.num_moves += 1
                if not self.is_filemode:
                    self.print_state()

            elif not self.file_over:
                self.board.switch_current_player()
                self.winner = self.board.current_player.name
                self.winner_reason = "Illegal move."
                self.game_over = True
        
        self.display_game_over()

    def get_input(self):
        if self.is_filemode:
            return self.next_file_command()
        else:
            return input()

    def next_file_command(self):
        if self.file_index >= len(self.file_commands):
            self.file_over = True
            return ""

        command = self.file_commands[self.file_index]
        self.file_index += 1
        return command
    
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
        piece = self.board.get_piece(src)

        if not piece:
            return False

        if self.board.is_checked(self.board.current_player):
            board_copy = self.board.try_move_piece(piece, dst)
            if board_copy.is_checked(board_copy.current_player):
                return False

        if promote and self.board.can_promote(piece, piece.coords, dst):
            if self.board.move_piece(piece, dst):
                return piece.promote()

        elif type(piece) == Pawn and self.board.can_promote(piece, piece.coords, dst):
            if self.board.move_piece(piece, dst):
                return piece.promote()

        elif not promote:
            return self.board.move_piece(piece, dst)

        return False
    
    def execute_drop(self, user_input):
        icon, dst = input_to_drop(user_input)
        current_player = self.board.current_player

        found_piece = None
        for piece in self.board.current_player.captures:
            if piece.icon.lower() == icon.lower():
                found_piece = piece
                break

        if self.board.is_checked(current_player):
            board_copy = self.board.try_drop_piece(current_player, found_piece, dst)
            if board_copy.is_checked(board_copy.current_player):
                return False

        return self.board.drop_piece(current_player, found_piece, dst)

        return False
    
    def print_state(self):
        """ Prints the state of the board along with metadata at current game iteration.
        """
        print(self.board.get_other_player_name(self.board.current_player.name) + 
              " player action: " + self.last_command.strip()) 
        print(self.board)
        self.print_metadata()
    
    def print_metadata(self):
        print("Captures UPPER: " + 
              " ".join([piece.icon for piece in self.board.players["UPPER"].captures]))
        print("Captures lower: " + 
              " ".join([piece.icon for piece in self.board.players["lower"].captures]))
        print()
        
        if self.board.is_checkmated(self.board.current_player):
            self.winner = self.board.get_other_player_name(self.board.current_player.name)
            self.winner_reason = "Checkmate."
            self.game_over = True

        if not self.game_over and self.board.current_player.num_moves > 199:
            print("Tie game.  Too many moves.")
            self.game_over = True

        if not self.game_over and self.board.is_checked(self.board.current_player):
            print(f"{self.board.current_player.name} player is in check!")
            self.print_available_moves()

        if not self.game_over:
            print(self.board.current_player.name + "> ", end="")
    
    def print_available_moves(self):
        """ Prints available moves to get out of check.
        """
        print("Available moves:")

        moves = get_moves_from_dict(self.board.get_uncheck_moves(self.board.current_player))
        drops = get_drops_from_dict(self.board.get_uncheck_drops(self.board.current_player))

        for drop in sorted(drops):
            print(drop)
        
        for move in sorted(moves):
            print(move)
    
    def display_game_over(self):
        self.print_state()
        if self.game_over and self.winner and self.winner_reason:
            print(self.winner + " player wins.  " + self.winner_reason)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", nargs="*", dest="filename", help="runs MiniShogi in file mode.")
    parser.add_argument("-i", "--interactive", action="store_true", help="runs MiniShogi in interactive mode.")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    game = Game(args.filename)
    game.play()