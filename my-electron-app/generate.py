import numpy as np
import random
from scipy.optimize import linprog
#Cell Constraint
A_cell = np.zeros((81, 729)) # 81 x 729 matrix of zeros
b_cell = np.ones(81) # 81 x 1 matrix of ones
given_numbers = []

for i in range(9):
    for j in range(9):
        row = i * 9  + j
        for k in range(9):
            col = 81 * i + 9 * j + k
            A_cell[row, col] = 1
#Row Constraint
A_row = np.zeros((81, 729)) # 81 x 729 matrix of zeros
b_row = np.ones(81) # 81 x 1 matrix of ones

for i in range(9):
    for k in range(9):
        row = i * 9  + k
        for j in range(9):
            col = 81 * i + 9 * j + k
            A_row[row, col] = 1
#Column Constraint       
A_col = np.zeros((81, 729)) # 81 x 729 matrix of zeros
b_col = np.ones(81) # 81 x 1 matrix of ones

for j in range(9):
    for k in range(9):
        row = j * 9  + k
        for i in range(9):
            col = 81 * i + 9 * j + k
            A_col[row, col] = 1
#Box Constraint
A_box = np.zeros((81, 729))  # 81 constraints (9 boxes × 9 numbers)
b_box = np.ones(81)

for box_x in range(3):
    for box_y in range(3):
        for k in range(9):
            row = (box_x * 3 + box_y) * 9 + k  # Constraint index
            for i in range(3):
                for j in range(3):
                    cell_x = box_x * 3 + i
                    cell_y = box_y * 3 + j
                    col = cell_x * 81 + cell_y * 9 + k  # Variable index
                    A_box[row, col] = 1
#Pre-filled numbers constraint
A_fixed = np.zeros((len(given_numbers), 729))  
b_fixed = np.ones(len(given_numbers))  

for idx, (r, c, v) in enumerate(given_numbers):
    col = r * 81 + c * 9 + (v - 1)
    A_fixed[idx, col] = 1
#Combine all constraints
A = np.vstack((A_cell, A_row, A_col, A_box, A_fixed))
b = np.hstack((b_cell, b_row, b_col, b_box, b_fixed))

def is_valid_move(board, row, col, num):
    """Check if num can be placed in board[row][col] without breaking Sudoku rules."""
    # Check the row
    if num in board[row]:
        return False

    # Check the column
    if num in board[:, col]:
        return False

    # Check the 3x3 sub-grid
    sub_row, sub_col = (row // 3) * 3, (col // 3) * 3
    if num in board[sub_row:sub_row+3, sub_col:sub_col+3]:
        return False

    return True

def solve_board(board):
    for row in range(9):
        for col in range(9):
            if board[row, col] == 0:
                for num in range(1, 10):
                    if is_valid_move(board, row, col, num):
                        board[row, col] = num
                        if solve_board(board):
                            return True
                        board[row, col] = 0
                return False  
    return True  

def generate(empty_cells = 40):
    board = np.zeros((9, 9), dtype=int)
    for i in range(0, 9, 3):
        nums = random.sample(range(1, 10), 9)
        board[i:i+3, i:i+3] = np.array(nums).reshape((3, 3))
        
    solve_board(board)
    
    cells = list(range(81))
    random.shuffle(cells)
    for i in range(empty_cells):
        row, col = divmod(cells.pop(), 9)
        board[row, col] = 0
    print(board)
    for row in range(9):
        for col in range(9):
            if board[row, col] != 0:
                given_numbers.append((row, col, int(board[row, col])))
    return board

generate()
