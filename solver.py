from puzzle_logic import PuzzleState

def manhattan_distance(board, size):
    distance = 0
    for i, tile in enumerate(board):
        if tile != 0:
            target_r, target_c = divmod(tile - 1, size)
            current_r, current_c = divmod(i, size)
            distance += abs(target_r - current_r) + abs(target_c - current_c)
    return distance

def linear_conflict(board, size):
    conflict = 0
    # Row conflict
    for r in range(size):
        row_tiles = []
        for c in range(size):
            tile = board[r * size + c]
            if tile != 0:
                target_r, target_c = divmod(tile - 1, size)
                if target_r == r:
                    row_tiles.append((tile, c, target_c))
        
        for i in range(len(row_tiles)):
            for j in range(i + 1, len(row_tiles)):
                if row_tiles[i][2] > row_tiles[j][2]: # target_c of left tile is > target_c of right tile
                    conflict += 2
                    
    # Column conflict
    for c in range(size):
        col_tiles = []
        for r in range(size):
            tile = board[r * size + c]
            if tile != 0:
                target_r, target_c = divmod(tile - 1, size)
                if target_c == c:
                    col_tiles.append((tile, r, target_r))
        
        for i in range(len(col_tiles)):
            for j in range(i + 1, len(col_tiles)):
                if col_tiles[i][2] > col_tiles[j][2]: # target_r of top tile is > target_r of bottom tile
                    conflict += 2
                    
    return conflict

def heuristic(state):
    return manhattan_distance(state.board, state.size) + linear_conflict(state.board, state.size)

def solve_puzzle(start_board, size=3):
    start_state = PuzzleState(start_board, size=size)
    if start_state.is_goal():
        return []

    threshold = heuristic(start_state)
    path = [start_state]
    
    while True:
        res, t = search(path, 0, threshold)
        if res == "FOUND":
            # Reconstruction is already in path
            return [node.board for node in path[1:]]
        if t == float('inf'):
            return None
        threshold = t

def search(path, g, threshold):
    node = path[-1]
    f = g + heuristic(node)
    if f > threshold:
        return None, f
    if node.is_goal():
        return "FOUND", f
    
    min_threshold = float('inf')
    for move in node.get_moves():
        if move not in path:
            path.append(move)
            res, t = search(path, g + 1, threshold)
            if res == "FOUND":
                return "FOUND", t
            if t < min_threshold:
                min_threshold = t
            path.pop()
    
    return None, min_threshold
