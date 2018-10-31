from utils import *

class Game:
	board = [[""]*5 for i in range(5)]

class Piece:
	def __init__(self, direction, position):
		self.position = position
		pass

	def is_valid_move(self, destination):
		pass

class King(Piece):
	offsets = [(-1, 1), (0, 1), 
			   (1, 1), (1, 0), 
			   (1, -1), (0, -1), 
			   (-1, -1), (-1, 0)]

class Rook(Piece):
	offsets = [(0, 1), (0, 2), 
		   	   (1, 0), (1, 2), 
		       (0, -1), (0, -2), 
		       (-1, 0), (-2, 0)]

class Bishop(Piece):
	offsets = [(-1, 1), (-2, 2), 
		       (1, 1), (2, 2), 
		       (1, -1), (2, -2), 
		       (-1, -1), (-2, 2)]

class GoldGeneral(Piece):
	offsets = [(-1, 1), (0, 1), 
		       (1, 1), (1, 0), 
		       (0, -1), (-1, 0)]

class SilverGeneral(Piece):
	offsets = [(-1, 1), (0, 1), 
		       (1, 1), (1, -1), 
		       (-1, -1)]

class Pawn(Piece):
	offsets = [(0, 1)]

class Player:
	pass	

if __name__ == "__main__":
	game = Game()
	p1, p2 = Player(), Player()