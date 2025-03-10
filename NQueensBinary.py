import math
from pysat.solvers import Glucose3

# Ký tự: ∨
# Sinh biến cho bảng cờ N-Queens
def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]

def at_least_one(clauses, variables):
    clauses.append(variables)

# RETURN:       - Y_vars : danh sách biến phụ tạo ra
#               - next_aux_var_updated: next_aux_var sau khi cấp phát.
def binary_amo(clauses, variables, next_aux_var):
    """
    Các bước:
      - Tính m = len(variables) và k = ceil(log2(m))
      - Tạo k biến phụ mới: Y_vars = [next_aux_var, ..., next_aux_var+k-1]
      - Với mỗi variables[i], gán cho nó một bit pattern (độ dài k) duy nhất (theo thứ tự từ 0 đến m-1).
      - Với mỗi bit, nếu bit = 1 : (-variables[i] ∨ Y_vars[b]),
                     nếu bit = 0 : (-variables[i] ∨ -Y_vars[b]).
    """

    m = len(variables)
    k = math.ceil(math.log2(m))

    # Tạo k biến phụ với ID từ next_aux_var đến next_aux_var+k-1
    Y_vars = list(range(next_aux_var, next_aux_var + k))
    next_aux_var_updated = next_aux_var + k

    # Sinh tất cả các bit pattern cho m biến, dùng thứ tự từ 0 đến m-1.
    # Dùng enumerate để lấy được cả chỉ số và giá trị phần tử trong danh sách, dễ cho viếc gán bit pattern cho mỗi biến
    for i, x in enumerate(variables):
        # Lấy bit pattern của số i, với độ dài k (số ít hơn sẽ được thêm số 0 bên trái)
        pattern = format(i, '0' + str(k) + 'b')
        for b in range(k):
            bit = int(pattern[b])
            if bit == 1:
                # (-variables[i] ∨ Y_vars[b])
                clauses.append([-x, Y_vars[b]])
            else:
                # (-variables[i] ∨ -Y_vars[b])
                clauses.append([-x, -Y_vars[b]])
    return Y_vars, next_aux_var_updated

# RETURN: trả về next_aux_var đã được cập nhật
def exactly_one_binary(clauses, variables, next_aux_var):
    at_least_one(clauses, variables)
    _, next_aux_var_updated = binary_amo(clauses, variables, next_aux_var)
    return next_aux_var_updated

# RETURN: Trả về các mệnh đề phù hợp để giả NQueens (clauses) 
#         và ID biến tiếp theo sau khi đã cấp phát các biến phụ (next_aux_var)
def generate_clauses(n, board):
    clauses = []

    # Các biến đã được tạo từ 1 đến n*n, do đó next_aux_var khởi đầu là n*n + 1.
    next_aux_var = n * n + 1

    # Hàng: mỗi hàng phải có chính xác 1 queen.
    for i in range(n):
        row_vars = board[i]
        next_aux_var = exactly_one_binary(clauses, row_vars, next_aux_var)

    # Cột: mỗi cột có Exactly one queen.
    for j in range(n):
        col_vars = [board[i][j] for i in range(n)]
        next_aux_var = exactly_one_binary(clauses, col_vars, next_aux_var)

    # Đường chéo chính (xuống phải) và đường chéo phụ (xuống trái).
    for i in range(n):
        for j in range(n):
            diag1 = []
            diag2 = []
            for k in range(1, n):
                if i + k < n and j + k < n:
                    diag1.append(board[i+k][j+k])
                if i + k < n and j - k >= 0:
                    diag2.append(board[i+k][j-k])
            if len(diag1) > 1:
                _, next_aux_var = binary_amo(clauses, diag1, next_aux_var)
            if len(diag2) > 1:
                _, next_aux_var = binary_amo(clauses, diag2, next_aux_var)
    return clauses, next_aux_var

# Hàm giải N-Queens sử dụng Binary Encoding
def solve_nqueens_binary(n):
    board = generate_variables(n)  # Ma trận bàn cờ n x n
    clauses, _ = generate_clauses(n, board)

    solver = Glucose3()
    for cl in clauses:
        solver.add_clause(cl)

    if solver.solve():
        model = solver.get_model()
        solution = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                var_id = board[i][j]
                if var_id in model:
                    solution[i][j] = 1
        return solution
    else:
        return None

def print_solution(solution):
    if solution is None:
        print("No solution found.")
    else:
        for row in solution:
            print(" ".join("Q" if cell else "." for cell in row))

n = 4 # Thay đổi kích thước theo ý muốn
solution = solve_nqueens_binary(n)
print_solution(solution)
