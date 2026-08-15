from Crypto.Util.number import long_to_bytes, isPrime

# Các giá trị từ đề bài
N = ... 
e = ...
c = ...

B = 1 << 256

# Phân tích N dựa trên cấu trúc: N = xy*B^2 + (x^2 + y^2)*B + xy
# Ta lấy phần dư và phần thương để tìm các thành phần
xy = N % B 
# N // B sẽ còn lại xy*B + (x^2 + y^2). Lấy tiếp % B để tách x^2 + y^2
x2_plus_y2 = (N // B) % B

# Ta có hệ thức:
# (x + y)^2 = x^2 + y^2 + 2xy
# (x - y)^2 = x^2 + y^2 - 2xy

sum_sq = x2_plus_y2 + 2 * xy
diff_sq = x2_plus_y2 - 2 * xy

# Tính căn bậc hai để tìm (x+y) và (x-y)
import math

def integer_sqrt(n):
    if n < 0: return None
    sqrt_n = math.isqrt(n)
    if sqrt_n * sqrt_n == n:
        return sqrt_n
    return None

x_plus_y = integer_sqrt(sum_sq)
x_minus_y = integer_sqrt(diff_sq)

if x_plus_y and x_minus_y:
    # Giải hệ phương trình tìm x, y:
    # x = ( (x+y) + (x-y) ) // 2
    # y = ( (x+y) - (x-y) ) // 2
    x = (x_plus_y + x_minus_y) // 2
    y = (x_plus_y - x_minus_y) // 2
    
    # Tính lại p và q từ x, y
    p = x * B + y
    q = y * B + x
    
    if p * q == N:
        phi = (p - 1) * (q - 1)
        d = pow(e, -1, phi)
        m = pow(c, d, N)
        print(long_to_bytes(m).decode())
    else:
        print("Không tìm thấy p, q chính xác.")
else:
    print("Không thể khai căn, kiểm tra lại dữ liệu N.")