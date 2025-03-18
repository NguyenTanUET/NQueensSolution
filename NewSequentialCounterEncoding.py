# Ký tự: ∨ ∀

def at_least_one(clauses, variables):
    clauses.append(variables)

# PARAMETERS:   - clauses: danh sách các clause CNF (mỗi clause là list[int]); các clause mới được thêm vào đây.
#               - X: danh sách các biến gốc (ID kiểu int) cần ràng buộc, X = [X1, X2, …, Xn]
#               - k: số nguyên > 0, ràng buộc rằng trong X có ít nhất không quá k biến được gán TRUE.
#               - next_aux: số hiệu biến tiếp theo để cấp phát biến phụ (auxiliary variables).
# RETURN:       - next_aux_updated: số hiệu biến tiếp theo sau khi cấp phát các biến phụ.
def new_sequential_counter(clauses, X, k, next_aux):
    """
    Mã hóa ràng buộc New Sequential Counter dựa trên bit-packing

    Ý tưởng:
      Đối với mỗi i (1 ≤ i ≤ n), ta tạo dãy biến phụ R[i] gồm min(i, k) phần tử.
      
      Với i = 1:
        (1) X[1] -> R[1][1]:  (-X[1] ∨ R[1][0])
        (5) -X[1] -> -R[1][1]:  (X[1] ∨ -R[1][0])
      
      Với i ≥ 2, với L = min(i+1, k):
        (2) ∀ j = 2,..., min(i, k):  R[i-1][j] -> R[i][j] : (-R[i-1][j] ∨ R[i][j])
        (3) ∀ j = 2,..., L:  (X[i] ∧ R[i-1][j-1]) -> R[i][j] : (-X[i] ∨ -R[i-1][j-1] ∨ R[i][j])
        (4) ∀ j = 1,..., min(|R[i-1]|, L):  (-X[i] ∧ -R[i-1][j]) -> -R[i][j] : (X[i] ∨ R[i-1][j] ∨ -R[i][j])
        (6) ∀ j = 2,..., L:  -R[i-1][j-1] -> -R[i][j] : (R[i-1][j-1] ∨ -R[i][j])
      
        (8) Cuối cùng, nếu n > k, thêm clause: (-R[n][k-1]) để đảm bảo tổng số TRUE không vượt quá k.
    """
    n = len(X)
    R = []  # R[i] sẽ chứa danh sách các biến phụ cho bộ đếm của X[1]...X[i].
    
    # i = 1 (cho X[0])
    r_vars = [next_aux]
    next_aux += 1
    R.append(r_vars)
    # Công thức (1)
    clauses.append([-X[0], r_vars[0]])
    # Công thức (5)
    clauses.append([X[0], -r_vars[0]])
    
    # Với i từ 2 đến n
    for i in range(1, n):
        L = min(i + 1, k)  # Số bit cho R[i] = min(i+1, k)
        r_vars = []
        for j in range(L):
            r_vars.append(next_aux)
            next_aux += 1
        R.append(r_vars)
        
        # Công thức (2)
        L_prev = min(len(R[i-1]), k)
        for j in range(1, L_prev):
            clauses.append([-R[i-1][j], R[i][j]])
        
        # Công thức (3)
        # Ở đây, index chuyển sang 0: với j từ 1 đến L-1, sử dụng R[i-1][j-1] để ảnh hưởng đến R[i][j]
        for j in range(1, L):
            if j - 1 < len(R[i-1]):
                clauses.append([-X[i], -R[i-1][j-1], R[i][j]])
        
        # Công thức (4)
        L_common = min(len(R[i-1]), L)
        for j in range(L_common):
            clauses.append([X[i], R[i-1][j], -R[i][j]])
        
        # Công thức (6)
        for j in range(1, L):
            if j - 1 < len(R[i-1]):
                clauses.append([R[i-1][j-1], -R[i][j]])
    
    # Công thứ (8)
    if n > k:
        clauses.append([-R[n-1][k-1]])
    
    return next_aux

def nsc_at_most_k(clauses, X, k, next_aux):
    return new_sequential_counter(clauses, X, k, next_aux)

def nsc_at_least_k(clauses, X, k, next_aux):
    """
    Mã hóa at least k dựa trên at most (n-k)
    """
    n = len(X)
    Y = [-x for x in X]
    # Số lượng biến Y đúng ≤ (n - k) <=> "at most (n - k)" constraint on Y.
    next_aux = new_sequential_counter(clauses, Y, n - k, next_aux)
    return next_aux

def nsc_exactly_k(clauses, X, k, next_aux):
    next_aux = nsc_at_most_k(clauses, X, k, next_aux)
    next_aux = nsc_at_least_k(clauses, X, k, next_aux)
    return next_aux

# Gọi 5 biến X1, X2, X3, X4, X5
X = [1, 2, 3, 4, 5]
clauses = []
next_aux = 6  # Các biến gốc có ID từ 1 đến 5, nên biến phụ bắt đầu từ 6.
    
# Ví dụ: Mã hoá ràng buộc "at most 2" trên X: ≤2 biến TRUE.
next_aux = nsc_at_most_k(clauses, X, 2, next_aux)
    
# In ra các clause đã sinh ra:
print("Các clause của NSC (At Most 2):")
for cl in clauses:
    print(cl)

