import numpy as np
import random
import json
from scipy.optimize import linprog
given_numbers = []
# Cell Constraint
A_cell = np.zeros((81, 729)) # 81 x 729 matrix of zeros
b_cell = np.ones(81) # 81 x 1 matrix of ones

for i in range(9):
    for j in range(9):
        row = i * 9  + j
        for k in range(9):
            col = 81 * i + 9 * j + k
            A_cell[row, col] = 1
# Row Constraint
A_row = np.zeros((81, 729)) # 81 x 729 matrix of zeros
b_row = np.ones(81) # 81 x 1 matrix of ones

for i in range(9):
    for k in range(9):
        row = i * 9  + k
        for j in range(9):
            col = i * 81 + j * 9 + k
            A_row[row, col] = 1
# Column Constraint       
A_col = np.zeros((81, 729)) # 81 x 729 matrix of zeros
b_col = np.ones(81) # 81 x 1 matrix of ones

for j in range(9):
    for k in range(9):
        row = j * 9  + k
        for i in range(9):
            col = i * 81 + j * 9 + k
            A_col[row, col] = 1
# Box Constraint
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
def solve_simplex(empty_cells):
    sudoku_board = generate(empty_cells)
    #Pre-filled numbers constraint
    A_fixed = np.zeros((len(given_numbers), 729))  
    b_fixed = np.ones(len(given_numbers))  
    
    # print(given_numbers)
    
    for idx, (r, c, v) in enumerate(given_numbers):
        col = r * 81 + c * 9 + (v - 1)
        A_fixed[idx, col] = 1
    #Combine all constraints
    A = np.vstack((A_cell, A_row, A_col, A_box, A_fixed))
    b = np.hstack((b_cell, b_row, b_col, b_box, b_fixed))
    
    result = linprog(c=np.zeros(729), A_eq=A, b_eq=b, method="highs")
    if not result.success:
        # print("Initial linear programming problem did not succeed.")
        generate(empty_cells)
        return solve_simplex(empty_cells)
    first_solution = np.round(result.x).astype(int)
    
    if not np.all(np.isclose(result.x, np.round(result.x))):
        # print("Fractional values found. The puzzle has multiple solutions.")
        generate(empty_cells)
        return solve_simplex(empty_cells)
    
    A_exclude = np.zeros((1, 729))
    for i in range(729):
        if first_solution[i] == 1:
            A_exclude[0, i] = 1
    b_exclude = np.array([80])
    
    result2 = linprog(
    c=np.zeros(729),
    A_eq=A,
    b_eq=b,
    A_ub=A_exclude,
    b_ub=b_exclude,
    method="highs"
)
    if result2.success:
        # print("Second linear programming problem succeeded.")
        generate(empty_cells)
        return solve_simplex(empty_cells)
    solved_board = reshape_board(extract_board(first_solution))
    return overlay_givens(solved_board, given_numbers)

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

def generate(empty_cells):
    given_numbers.clear()
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
    # print(board)
    for row in range(9):
        for col in range(9):
            if board[row, col] != 0:
                given_numbers.append((row, col, int(board[row, col])))
    return board

def reshape_board(board):
    reshaped_board = board.reshape(3, 3, 3, 3)
    reshaped_board = reshaped_board.transpose((0, 2, 1, 3))
    reshaped_board = reshaped_board.reshape(9, 9)
    return reshaped_board

def extract_board(solution_vector):
    board = np.zeros((9, 9), dtype=int)
    for cell in range(81):
        row, col = divmod(cell, 9)
        block = solution_vector[cell*9:(cell+1)*9]
        digit = np.argmax(block) + 1
        board[row, col] = digit
    return board
def overlay_givens(solved_board, given_numbers):
    """
    Sets non-given cells to 0
    """
    masked_board = np.zeros((9, 9), dtype=int)
    for (r, c, v) in given_numbers:
        masked_board[r, c] = v
    return masked_board

if __name__ == "__main__":
    empty_cells = 40
    generate(empty_cells)
    board = solve_simplex(empty_cells)
    print(json.dumps(board.tolist()))