from pysat.solvers import Glucose3

# Ký tự: ∨
# Sinh biến cho bảng cờ N-Queens
def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]

def at_least_one(clauses, variables):
    clauses.append(variables)

# Mã hoá AMO theo binomial
def at_most_one_binomial(clauses, variables):
    for i in range(len(variables)):
        for j in range(i+1, len(variables)):
            clauses.append([-variables[i], -variables[j]])

def exactly_one_binomial(clauses, variables):
    at_least_one(clauses, variables)
    at_most_one_binomial(clauses, variables)

# RETURN: trả về next_var_updated sau khi đã cấp phát các biến chỉ huy.
def commander_exactly_one(clauses, variables, group_size, next_aux_var):
    """
    Các bước:
      1. Chia tập biến 'variables' thành các nhóm (group) có kích thước 'group_size'
         (nhóm cuối có thể nhỏ hơn nếu không chia hết).
      2. Với mỗi nhóm, giới thiệu một biến chỉ huy (commander variable) có ID bắt đầu từ next_aux_var.
      3. Cho mỗi biến x trong một nhóm, thêm clause: (¬x ∨ c)  => nếu x được chọn thì commander c phải đúng.
      4. Thêm clause: (x1 ∨ x2 ∨ ... ∨ x_k ∨ ¬c) cho nhóm đó, đảm bảo nếu c không đúng thì không có x nào được chọn.
      5. Sau đó, trên tập các biến chỉ huy vừa tạo ra, thêm ràng buộc "exactly one" (ở đây dùng binomial):
            - ALO: (c1 ∨ c2 ∨ ... ∨ c_m)
            - AMO: với mọi cặp (ci, cj), thêm (¬ci ∨ ¬cj)
    """
    # Chia các biến thành các nhóm
    # groups là một danh sách các sublist, mỗi sublist chứa một nhóm các biến. 
    # Ví dụ, nếu variables = [1,2,3,4,5,6,7,8,9,10] và group_size = 3, thì kết quả sẽ là
    # groups = [[1,2,3], [4,5,6], [7,8,9], [10]]
    groups = [variables[i:i+group_size] for i in range(0, len(variables), group_size)]
    commander_vars = []
    for group in groups:
        # Cấp phát biến chỉ huy cho nhóm hiện tại
        commander = next_aux_var
        next_aux_var += 1
        commander_vars.append(commander)
        # Với mỗi biến x trong nhóm, nếu x đúng thì commander phải đúng.
        for x in group:
            clauses.append([-x, commander])
        # Nếu commander không đúng thì phải có ít nhất một x đúng trong nhóm.
        # Clause: (x1 ∨ x2 ∨ ... ∨ x_k ∨ ¬commander)
        group_clause = group[:]  # sao chép danh sách biến của nhóm
        group_clause.append(-commander)
        clauses.append(group_clause)
    
    # Ràng buộc "exactly one" trên các biến chỉ huy
    at_least_one(clauses, commander_vars)
    at_most_one_binomial(clauses, commander_vars)
    
    return next_aux_var

# RETURN: Trả về các mệnh đề phù hợp để giả NQueens (clauses) 
def generate_clauses(n, board, group_size=3):
    clauses = []

    # Các biến đã được tạo từ 1 đến n*n, do đó next_aux_var khởi đầu là n*n + 1.
    next_aux_var = n * n + 1 

    # Hàng: mỗi hàng phải có chính xác 1 queen.
    for i in range(n):
        row_vars = board[i]
        next_aux_var = commander_exactly_one(clauses, row_vars, group_size, next_aux_var)

    # Cột: mỗi cột có Exactly one queen.
    for j in range(n):
        col_vars = [board[i][j] for i in range(n)]
        exactly_one_binomial(clauses, col_vars)
    
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
                at_most_one_binomial(clauses, diag1)
            if len(diag2) > 1:
                at_most_one_binomial(clauses, diag2)

    return clauses

# Hàm giải N-Queens sử dụng Commander Encoding
def solve_nqueens(n, group_size=3):
    board = generate_variables(n)
    clauses = generate_clauses(n, board, group_size)

    solver = Glucose3()
    for cl in clauses:
        solver.add_clause(cl)
    
    if solver.solve():
        model = solver.get_model()
        solution = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                var = board[i][j]
                if var in model:
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

    n = 4   # Thay đổi kích thước theo ý muốn
    # group_size xác định kích thước nhóm dùng trong commander encoding cho mỗi hàng.
    # Ví dụ, nếu group_size = 2, mỗi hàng sẽ được chia thành các nhóm có 2 biến (ngoại lệ nhóm cuối có thể nhỏ hơn).
    solution = solve_nqueens(n, group_size=2)
    print_solution(solution)

