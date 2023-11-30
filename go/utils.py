import numpy as np


def flood_fill(i,j,board):     # returns the captured group or None if there isn't one
    has_liberties, group_positions = _flood_fill(i,j,board[i][j],board)
    if has_liberties:
        return None
    else:
        return group_positions

# helper method that returns True if this position or an adjacent position to this one has at least one adjacent empty position (liberty),
# otherwise it returns False and also returns all the positions of the captured group to which the position (i,j) belongs
def _flood_fill(i,j,original_piece,board,group_positions=set(),visited=set()):
    if i < 0 or i >= len(board) or j < 0 or j >= len(board) or (i, j) in visited: 
        return False, group_positions    # returns False if this position is out of bounds or was already visited

    visited.add((i, j))
    position = board[i][j]

    if position == 0:
        return True, group_positions            # this position is a liberty of the initially given position
    elif position == -original_piece:
        return False, group_positions           # this position has an opposing piece to the original position being checked

    neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]      # if (i,j) has the same Piece as the original position, its neighbors will be checked
    for i,j in neighbors:
        result, group_positions = _flood_fill(i,j,original_piece,board,group_positions,visited)
        if result:
            return True, group_positions
    group_positions.add((i,j))      # this position has a same color piece as the original position being checked and it has no liberties
    return False, group_positions

def flood_fill_example():
    # Example usage:
    board = np.array([
        [1, 1, -1, 0],
        [-1, 1, 1, -1],
        [1, -1, -1, 0],
        [0, 0, 0, 0]
    ])
    
    row = 1
    col = 0

    captured_group = flood_fill(row, col, board)
    print(captured_group)
    if captured_group:
        print(len(captured_group))

# returns the positions of the captured group (i,j) belongs to and which player is the captor. if (i,j) isn't captured, return None
def get_captured_territories(i,j,board): 
    ct_group = set()
    captor = 0 ######
    ######
    return ct_group, captor


flood_fill_example()