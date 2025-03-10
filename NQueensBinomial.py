from pysat.solvers import Glucose3

# Trả về ma trận n x n , EX: n = 3 ->  [1, 2, 3],
#                                       [4, 5, 6],
#                                       [7, 8, 9]
def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]

def at_least_one(clauses, variables):
    clauses.append(variables)

# PARAMETERS: 
#   clauses: danh sách các mệnh đề đang có
#   variables: danh sách các biến để add theo format AMO
# RETURN: cập nhật danh sách các mệnh đề sau khi đã add các biến theo AMO
def at_most_one(clauses, variables):
    for i in range(0, len(variables)):
        for j in range(i + 1, len(variables)):
            clauses.append([-variables[i], -variables[j]])      # AMO(-xi, -xj)
    return clauses

# PARAMETERS:
#   clauses: danh sách các mệnh đề đang có
#   variables: danh sách các biến để add theo format AMO
def exactly_one(clauses, variables):
    at_least_one(clauses, variables)        
    at_most_one(clauses, variables)     

# PARAMETERS:
#   n: số lượng hậu
#   board: ma trận n x n trước khi chạy hàm này
# RETURN: trả về các mệnh đề phù hợp theo CNF để giải bài toán NQueens
def generate_clauses(n, board):
    clauses = []

    # Hàng: mỗi hàng có Exactly one queen.
    for i in range(n):        
        row_vars = board[i]
        exactly_one(clauses, row_vars)

    # Cột: mỗi cột có Exactly one queen.
    for j in range(n):
        col_vars = [board[i][j] for i in range(n)]
        exactly_one(clauses, col_vars)

    # Đường chéo chính (xuống phải) và đường chéo phụ (xuống trái).
    for i in range(n):
        for j in range(n):
            for k in range(1, n):
                if i + k < n and j + k < n:
                    at_most_one(clauses, [board[i][j], board[i + k][j + k]])
                if i + k < n and j - k >= 0:
                    at_most_one(clauses, [board[i][j], board[i + k][j - k]])

    return clauses

# Hàm giải N-Queens sử dụng Binomial Encoding
def solve_n_queens(n):
    board = generate_variables(n)           # Ma trận bàn cờ n x n
    clauses = generate_clauses(n, board)    # Danh sách các mệnh đề để giải NQueens
    print(clauses)

    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    if solver.solve():
        model = solver.get_model()              # Nếu SATISFIABLE, trả về model hợp lý (Ex: [1, -2, 3, ...])
        return [[int(model[i * n + j] > 0) for j in range(n)] for i in range(n)] # Trả về ma trận bàn cờ theo model ở trên (Ex: [1, -2, 3]
    else:                                                                        #                                              [4, 5, -6]
        return None                                                              #                                              [-7, 8, 9])


def print_solution(solution):
    if solution is None:
        print("No solution found.")
    else:
        print(solution)
        for row in solution:
            print(" ".join("Q" if cell else "." for cell in row))


n = 4
# print(generate_clauses(n, generate_variables(n)))
solution = solve_n_queens(n)
print_solution(solution)
