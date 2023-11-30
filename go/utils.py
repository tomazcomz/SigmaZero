import numpy as np


def invalid_position(i,j,n):    # helper method that returns True if (i,j) is an invalid position
    return i < 0 or i >= n or j < 0 or j >= n


def flood_fill(i,j,board):     # returns the captured group or None if there isn't one
    has_liberties, group_positions = _flood_fill(i,j,board[i][j],board)
    if has_liberties:
        return None
    else:
        return group_positions

# helper method that returns True if this position or an adjacent position to this one has at least one adjacent empty position (liberty),
# otherwise it returns False and also returns all the positions of the captured group to which the position (i,j) belongs
def _flood_fill(i,j,original_piece,board,group_positions=set(),visited=set()):
    if (i,j) in visited or invalid_position(i,j,len(board)):
        return False, group_positions    # returns False if this position is out of bounds or was already visited

    visited.add((i, j))
    position = board[i][j]

    if position == 0:
        return True, group_positions            # this position is a liberty of the initially given position
    elif position == -original_piece:
        return False, group_positions           # this position has an opposing piece to the original position being checked

    neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]    # if (i,j) has the same piece as the original position, its neighbors will be checked
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
    ct_group, captor = _get_captured_territories(i,j,board)
    return ct_group, captor

# recursive helper method that implements an algorithm that searches for a captured group of territories
def _get_captured_territories(i,j,board,ct_group=set(),captor=0,visited=set()):
    if (i,j) in visited or invalid_position(i,j,len(board)):
        return ct_group, captor
    visited.add((i,j))
    if board[i][j] != 0:    # if this position isn't empty, it checks whose player it belongs to
        if captor == 0:
            captor = board[i][j]     # getting the captor of this group, if there isn't one yet
            return ct_group, captor
        elif board[i][j]!=captor:    # If there's two different captors to the group's positions, then
            return None,0   # it returns None, because there's no group captured by one captor
        return ct_group, captor     # this piece is captured by the same captor as every piece in this group checked so far
    ct_group.add((i,j))  # if this position is empty, then it is added to the territory group
    neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]   # if (i,j) has the same piece as the original position, its neighbors will be checked
    for x,y in neighbors:
        ct_group,captor = _get_captured_territories(x,y,board,ct_group,captor,visited)
    # (continue from here)
    
def get_captured_territories_example():
    board = np.array([
        [0,-1,-1,0],
        [-1,1,1,0],
        [0,0,0,0],
        [1,0,0,1]
    ])
    i=0
    j=0
    ct_group, captor = _get_captured_territories(i,j,board)
    print(ct_group)
    print(f"captor: {captor}")
    
get_captured_territories_example()


# The point A is adjacent to a black stone. Therefore, A does not belong to White's territory. 
# However, A is connected to B (by the path shown in the diagram, among others), which is adjacent to a white stone. 
# Therefore, A does not belong to Black's territory either. In conclusion, A is neutral territory.
# An empty point only belongs to somebody's territory, 
#   if all the empty intersections that form a connected group with it are adjacent to stones of that player's territory