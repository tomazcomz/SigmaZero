import numpy as np

def flood_fill(i,j,board):
    return _flood_fill(i,j,board[i][j],board)

def _flood_fill(i,j,stone_color,board,visited=set()):    # returns True if this position or a adjacent position to this one has at least one adjacent empty position (liberty)
    if i < 0 or i >= len(board) or j < 0 or j >= len(board) or (i, j) in visited:        # checks whether the position is out of bounds
        return False

    visited.add((i, j))
    stone = board[i][j]

    if stone == 0:
        return True             # this position is a liberty of the initially given position
    elif stone == -stone_color:
        return False            # this position has an opposing piece to the original position being checked

    neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]        # if this position has the same piece as the original position, its neighbors will be checked
    for i,j in neighbors:
        result = flood_fill(i,j,stone_color,board,visited)
        if result:
            return True
    return False



def flood_fill_example():
    # Example usage:
    board = np.array([
        [0, 0, 0, 0],
        [0, 0, 1, 1],
        [0, 0, -1, -1],
        [0, 0, 1, 1]
    ])
    
    row = 2
    col = 2
    color = -1

    result = not flood_fill(row, col, color, board)
    print(f'Is the position ({row}, {col}) part of a captured group?\n -> {result}')

flood_fill_example()