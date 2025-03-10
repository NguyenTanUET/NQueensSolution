import math
from pysat.solvers import Glucose3

# Ký tự: ∨
# Sinh biến cho bảng cờ N-Queens
def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]

def at_least_one(clauses, variables):
    clauses.append(variables)

#RETURN: trả về next_aux_var sau khi đã cấp phát các biến phụ.
def product_amo(clauses, variables, next_aux_var):
    """
    Các bước:
      - Tính số lượng biến m = len(variables)
      - Chọn p = ceil(sqrt(m)) và q = ceil(m/p)
      - Tạo p biến phụ cho hàng: r_0,..., r_{p-1} với ID từ next_aux_var.
      - Tạo q biến phụ cho cột: c_0,..., c_{q-1} với ID tiếp theo.
      - Với mỗi variables[i], gán vị trí: row = i // q, col = i mod q, và thêm:
            (-variables[i] ∨ r_row) và (-variables[i] ∨ c_col)
      - Với các biến r và c (số lượng nhỏ), thêm các clause AMO theo binomial:
            với mọi cặp r_i, r_j: (-r_i ∨ -r_j) và tương tự với c.
    """
    m = len(variables)

    p = math.ceil(math.sqrt(m))
    q = math.ceil(m / p)
    
    # Tạo biến phụ cho hàng: r_0 ... r_{p-1}
    r_vars = list(range(next_aux_var, next_aux_var + p))
    next_aux_var += p
    # Tạo biến phụ cho cột: c_0 ... c_{q-1}
    c_vars = list(range(next_aux_var, next_aux_var + q))
    next_aux_var += q
    
    # Liên kết mỗi variables[i] với r_vars và c_vars
    for i, x in enumerate(variables):
        row = i // q
        col = i % q
        clauses.append([-x, r_vars[row]])
        clauses.append([-x, c_vars[col]])
    
    # Áp dụng AMO cho các biến r
    for i in range(len(r_vars)):
        for j in range(i+1, len(r_vars)):
            clauses.append([-r_vars[i], -r_vars[j]])

    # Áp dụng AMO cho các biến c
    for i in range(len(c_vars)):
        for j in range(i+1, len(c_vars)):
            clauses.append([-c_vars[i], -c_vars[j]])
    
    return next_aux_var

# RETURN: trả về next_aux_var đã được cập nhật
def exactly_one_product(clauses, variables, next_aux_var):
    at_least_one(clauses, variables)
    next_aux_var = product_amo(clauses, variables, next_aux_var)
    return next_aux_var

# RETURN: Trả về các mệnh đề phù hợp để giả NQueens (clauses) 
#         và ID biến tiếp theo sau khi đã cấp phát các biến phụ (next_aux_var)
def generate_clauses(n, board):
    clauses = []

    # Các biến đã được tạo từ 1 đến n*n, do đó next_aux_var khởi đầu là n*n + 1.
    next_aux_var = n * n + 1 
    
    # Hàng: mỗi hàng phải có chính xác 1 queen.
    for i in range(n):
        row_vars = board[i]
        next_aux_var = exactly_one_product(clauses, row_vars, next_aux_var)
    
    # Cột: mỗi cột có Exactly one queen.
    for j in range(n):
        col_vars = [board[i][j] for i in range(n)]
        next_aux_var = exactly_one_product(clauses, col_vars, next_aux_var)
    
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
                next_aux_var = product_amo(clauses, diag1, next_aux_var)
            if len(diag2) > 1:
                next_aux_var = product_amo(clauses, diag2, next_aux_var)
    
    return clauses, next_aux_var

# Hàm giải N-Queens sử dụng Product Encoding
def solve_nqueens_product(n):
    board = generate_variables(n)
    clauses, _ = generate_clauses(n, board)
    
    solver = Glucose3()
    for cl in clauses:
        solver.add_clause(cl)
    
    if solver.solve():
        model = solver.get_model()
        solution = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if board[i][j] in model:
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


n = 4  # Thay đổi kích thước theo ý muốn
solution = solve_nqueens_product(n)
print_solution(solution)

