import numpy as np

def flood_fill(i,j,board):     # returns the size of the captured group or 0 if there isn't one
    has_liberties, size = _flood_fill(i,j,board[i][j],board)
    is_captured = not has_liberties
    return size if is_captured else 0

# helper method that returns True if this position or an adjacent position to this one has at least one adjacent empty position (liberty),
# otherwise it returns False and also calculates the size of the captured group to which the position (i,j) belongs
def _flood_fill(i,j,stone_color,board,visited=set(),captured_group_size=0):
    if i < 0 or i >= len(board) or j < 0 or j >= len(board) or (i, j) in visited: 
        return False, captured_group_size    # returns False if this position is out of bounds or was already visited

    visited.add((i, j))
    stone = board[i][j]

    if stone == 0:
        return True, captured_group_size            # this position is a liberty of the initially given position
    elif stone == -stone_color:
        return False, captured_group_size           # this position has an opposing piece to the original position being checked

    neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]      # if (i,j) has the same piece as the original position, its neighbors will be checked
    for i,j in neighbors:
        result, captured_group_size = _flood_fill(i,j,stone_color,board,visited,captured_group_size)
        if result:
            return True, captured_group_size
    captured_group_size += 1
    print("captured group piece")   # this command is called exactly the same number of times as the number of pieces belonging to the captured group
    return False, captured_group_size


def flood_fill_example():
    # Example usage:
    board = np.array([
        [-1, -1, -1, 1],
        [-1, 1, 1, 1],
        [-1, -1, -1, -1],
        [-1, -1, 1, 1]
    ])
    
    row = 1
    col = 2
    color = 1

    result, size = _flood_fill(row, col, color, board)
    print(f'Is the position ({row}, {col}) part of a captured group?\n -> {not result}\n Size: {size}')


flood_fill_example()