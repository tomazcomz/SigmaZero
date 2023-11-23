def flood_fill(i,j,board,visited=set()):    # returns True if this position or a adjacent position to this one has at least one adjacent empty position (liberty)
    if i < 0 or i >= len(board) or j < 0 or j >= len(board[0]) or (i, j) in visited:
        return False

    visited.add((i, j))
    stone = board[i][j]

    if stone == 0:
        return True  # This position is a liberty of the initially given position.

    neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
    
    
    return all(flood_fill(i, j, board, visited) for i,j in neighbors)


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
