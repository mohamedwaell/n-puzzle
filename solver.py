import heapq
from puzzle_logic import PuzzleState

def manhattan_distance(board):
    distance = 0
    for i, tile in enumerate(board):
        if tile != 0:
            # Goal position for tile (tile - 1)
            target_r, target_c = divmod(tile - 1, 3)
            current_r, current_c = divmod(i, 3)
            distance += abs(target_r - current_r) + abs(target_c - current_c)
    return distance

def solve_puzzle(start_board):
    start_state = PuzzleState(start_board)
    if start_state.is_goal():
        return []

    # Priority Queue elements: (f_score, PuzzleState)
    pq = [(manhattan_distance(start_board), start_state)]
    visited = {tuple(start_board): 0}
    
    while pq:
        f, current_state = heapq.heappop(pq)
        
        if current_state.is_goal():
            # Reconstruct path
            path = []
            while current_state.parent:
                path.append(current_state.board)
                current_state = current_state.parent
            return path[::-1] # Return boards from start to goal

        for next_state in current_state.get_moves():
            board_tuple = tuple(next_state.board)
            if board_tuple not in visited or next_state.depth < visited[board_tuple]:
                visited[board_tuple] = next_state.depth
                h = manhattan_distance(next_state.board)
                heapq.heappush(pq, (next_state.depth + h, next_state))
                
    return None # No solution (shouldn't happen for solvable puzzles)
