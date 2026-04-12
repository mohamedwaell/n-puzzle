import random

class PuzzleState:
    def __init__(self, board, parent=None, move="", depth=0):
        self.board = board  # List of 9 integers, 0 is the empty tile
        self.parent = parent
        self.move = move
        self.depth = depth
        self.blank_index = self.board.index(0)

    def is_goal(self):
        return self.board == [1, 2, 3, 4, 5, 6, 7, 8, 0]

    def get_moves(self):
        moves = []
        r, c = divmod(self.blank_index, 3)
        
        # Possible moves: (row_change, col_change, direction_name)
        directions = [(-1, 0, "Up"), (1, 0, "Down"), (0, -1, "Left"), (0, 1, "Right")]
        
        for dr, dc, name in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_blank_index = nr * 3 + nc
                new_board = list(self.board)
                new_board[self.blank_index], new_board[new_blank_index] = new_board[new_blank_index], new_board[self.blank_index]
                moves.append(PuzzleState(new_board, parent=self, move=name, depth=self.depth + 1))
        
        return moves

    def __lt__(self, other):
        # Needed for priority queue in A*
        return False

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple(self.board))

def get_inversions(board):
    inversions = 0
    tiles = [tile for tile in board if tile != 0]
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions

def is_solvable(board):
    return get_inversions(board) % 2 == 0

def generate_solvable_puzzle():
    while True:
        board = list(range(9))
        random.shuffle(board)
        if is_solvable(board) and board != [1, 2, 3, 4, 5, 6, 7, 8, 0]:
            return board
