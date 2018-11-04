from utils import input_to_coords, stringify_board

class Piece:

	def __init__(self, direction, position, board):
		""" Initializes piece
		"""
		self.direction = direction
		self.position = position
		self.board = board

		if self.direction == "lower":
			self.icon = self.icon.lower()


	def move(self, src, dest):
		""" Move a piece from start to destination if valid move.
		"""

		# TODO: change to function get_piece ?
		piece = self.board.grid[src[0]][src[1]]
		if self.is_valid_move(src, dest):
			self.board.grid[src[0]][src[1]] = ""
			self.board.grid[dest[0]][dest[1]] = piece
		else:
			print("INVALID MOVE")

	def is_valid_move(self, src, dst):
		""" Determines
		"""
		return True


class King(Piece):

	icon = "K"
	moves = [(-1, 1), (0, 1), 
		 (1, 1), (1, 0), 
		 (1, -1), (0, -1), 
		 (-1, -1), (-1, 0)]


class Rook(Piece):

	icon = "R"
	moves = [(0, 1), (0, 2), 
		   	 (1, 0), (1, 2), 
		     (0, -1), (0, -2), 
		     (-1, 0), (-2, 0)]


class Bishop(Piece):

	icon = "B"
	moves = [(-1, 1), (-2, 2), 
		     (1, 1), (2, 2), 
		     (1, -1), (2, -2), 
		     (-1, -1), (-2, 2)]


class GoldGeneral(Piece):

	icon = "G"
	moves = [(-1, 1), (0, 1), 
		     (1, 1), (1, 0), 
		     (0, -1), (-1, 0)]


class SilverGeneral(Piece):

	icon = "S"
	moves = [(-1, 1), (0, 1), 
		     (1, 1), (1, -1), 
		     (-1, -1)]

class Pawn(Piece):

	icon = "P"
	moves = [(0, 1)]

class Board:

	def __init__(self):
		""" Initializes board.
		"""
		self.grid = [[""]*5 for i in range(5)]
		self.players = []
		self.populate_grid()

	def place_piece(self, piece, coords):
		""" Places Piece at position coords on this Board's grid
		"""
		self.grid[coords[0]][coords[1]] = piece

	def get_piece(self, coords):
		""" Returns Piece if it exists at these coords
		"""
		return self.grid[coords[0]][coords[1]]

	def remove_piece(self, coords):
		""" Removes piece from grid if it exists at these coords
		"""
		self.grid[coords[0]][coords[1]] = ""

	def populate_grid(self):
		""" Populates pieces of initial board state.
		"""
		pieces = [King, GoldGeneral, SilverGeneral, Bishop, Rook]

		# index into row col
		for i in range(5):
			# TODO: Abstract piece placement to function
			self.place_piece(pieces[i]("UPPER", (4 - i, 4), self), (4 - i, 4))
			self.place_piece(pieces[i]("lower", (i, 0), self), (i, 0))

		# place pawns
		self.place_piece(Pawn("UPPER", (0, 3), self), (0, 3))
		self.place_piece(Pawn("lower", (4, 1), self), (4, 1))

if __name__ == "__main__":
	board = Board()
	game_over = False
	is_lower_turn = True
	while not game_over:
		print(stringify_board(board.grid))
		if is_lower_turn:
			user_input = input("lower> ")
		else:
			user_input = input("UPPER> ")

		src, dest = input_to_coords(user_input)
		piece = board.get_piece(src)
		piece.move(src, dest)
		# make move here