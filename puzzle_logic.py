import random

class PuzzleState:
    def __init__(self, board, size=3, parent=None, move="", depth=0):
        self.board = board  # List of integers, 0 is the empty tile
        self.size = size
        self.parent = parent
        self.move = move
        self.depth = depth
        self.blank_index = self.board.index(0)

    def is_goal(self):
        # Goal: [1, 2, ..., size*size-1, 0]
        goal = list(range(1, self.size * self.size)) + [0]
        return self.board == goal

    def get_moves(self):
        moves = []
        r, c = divmod(self.blank_index, self.size)
        
        # Possible moves: (row_change, col_change, direction_name)
        directions = [(-1, 0, "Up"), (1, 0, "Down"), (0, -1, "Left"), (0, 1, "Right")]
        
        for dr, dc, name in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                new_blank_index = nr * self.size + nc
                new_board = list(self.board)
                new_board[self.blank_index], new_board[new_blank_index] = new_board[new_blank_index], new_board[self.blank_index]
                moves.append(PuzzleState(new_board, size=self.size, parent=self, move=name, depth=self.depth + 1))
        
        return moves

    def __lt__(self, other):
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

def is_solvable(board, size):
    inversions = get_inversions(board)
    if size % 2 != 0:
        return inversions % 2 == 0
    else:
        # For even size (like 4x4)
        blank_idx = board.index(0)
        blank_row = blank_idx // size
        blank_row_from_bottom = size - blank_row
        # Goal state [1, ..., 0] has 0 inversions and blank in row 1 from bottom (sum 1, odd)
        return (inversions + blank_row_from_bottom) % 2 == 1

def generate_solvable_puzzle(size=3):
    goal = list(range(1, size * size)) + [0]
    while True:
        board = list(range(size * size))
        random.shuffle(board)
        if is_solvable(board, size) and board != goal:
            return board
