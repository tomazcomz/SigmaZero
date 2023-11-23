def flood_fill(i,j,stone_color,board,visited=set()):    # returns True if this position or a adjacent position to this one has at least one adjacent empty position (liberty)
    if i < 0 or i >= len(board) or j < 0 or j >= len(board[0]) or (i, j) in visited:        # checks whether the position is out of bounds
        return False

    visited.add((i, j))
    stone = board[i][j]

    if stone == 0:
        return True             # this position is a liberty of the initially given position
    elif stone == -stone_color:
        return False            # this position has an opposing piece to the original position being checked

    neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]        # if this position has the same piece as the original position, its neighbors will be checked
    return not all(not flood_fill(i, j, board, visited) for i,j in neighbors)   # returns True if at least one adjacent position to the group of the same color has a liberty


# Example usage:
board = [
    [0, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 1, 2, 0],
    [0, 0, 1, 0]
]

row = 2
col = 2

result = not flood_fill(row, col, board)
print(f'Is the position ({row}, {col}) part of a captured group?\n -> {result}')
