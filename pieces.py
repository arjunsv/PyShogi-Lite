class Piece:

    num_pieces = 0

    def __init__(self, player_name, coords, icon, blockable, copy):
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
        """ Property that returns the correct icon conditional on the player_name and is_promoted.
        """
        ret_icon = self._icon
        if self.player_name == "lower":
            ret_icon = self._icon.lower()
        if self.is_promoted:
            ret_icon = "+" + ret_icon
        return ret_icon
    
    @staticmethod
    def from_icon(icon, coords=(-1, -1)):
        """ Returns a new piece corresponding from a piece icon.
        """
        icon_to_piece = {'k': King, 'g': GoldGeneral, 's': SilverGeneral, 
                         'b': Bishop, 'r': Rook, 'p': Pawn}

        stripped_icon = icon.strip("+")
        player_name = "UPPER" if stripped_icon.isupper() else "lower"
        stripped_icon = stripped_icon.lower()
        piece = icon_to_piece[stripped_icon](player_name, coords)

        if "+" in icon:
            piece.promote()

        return piece

    def copy(self):
        """ Returns a copy of the piece with the same id as the original piece.
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
        """ Equality comparator for pieces based on unique id.
        """
        return type(self) == type(other) and self.id == other.id

    def __hash__(self):
        """ Hash function for pieces based on unique id.
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
        self.unblockable_moves = self.unblockable_moves + King.unblockable_moves
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
        self.unblockable_moves = self.unblockable_moves + King.unblockable_moves
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