import math
from itertools import combinations


class CustomException(Exception):
    def __init__(self, message):
        self.message = message;


def reverse(a, b):
    if math.gcd(a, b) != 1:
        raise CustomException(math.gcd(a, b))
    n = b
    res = 1
    prev = 0
    i = 0
    while a != 1:
        temp = res
        res = res * (b // a) + prev
        prev = temp
        a_1 = b%a
        b = a
        a = a_1
        i += 1
    return res if i % 2 == 0 else -res+n


def zero_poly(f):
    while f and f[-1] == 0:
        f.pop()
    if not f:
        return [0]
    return f


def poly_div_2(f, g):
    r = list(f)
    m = len(f) - 1
    h = len(g) - 1
    q = [0] * (m - h + 1)
    counter = 0
    for k in range(m - h, -1, -1):
        counter += 1
        q[k] = r[h + k] & g[h]
        for j in range(h + k, k - 1, -1):
            r[j] = r[j] ^ (q[k] & g[j - k])
    return zero_poly(q), zero_poly(r)


def poly_mul_2(f, g):
    m = len(f) - 1
    h = len(g) - 1
    q = [0] * (m + h + 1)
    for i in range(h + 1):
        for j in range(m + 1):
            q[i + j] = q[i + j] ^ (g[i] & f[j])
    return zero_poly(q)


def poly_sum_2(f, g):
    if f == [0]:
        return g
    if g == [0]:
        return f
    if len(g) > len(f):
        return poly_sum_2(g, f)
    m = len(f) - 1
    h = len(g) - 1
    q = [0] * (m + 1)
    for i in range(h + 1):
        q[i] = f[i] ^ g[i]
    for i in range(h + 1, m + 1):
        q[i] = f[i]
    return zero_poly(q)


def poly_euclid_2(f, g):
    if len(g) > len(f):
        return poly_euclid_2(g, f)
    while g != [0]:
        q, r = poly_div_2(f, g)
        f = g
        g = r
    return f


def poly_step_2(f, e):
    if e == 0:
        return [1]
    if e == 1:
        return f
    s = [1]
    while e > 1:
        if e % 2 == 1:
            s = poly_mul_2(s, f)
        f = poly_mul_2(f, f)
        e = e // 2
    return poly_mul_2(f, s)


def calc_poly(f, v, base, module):
    res = [f[0]]
    for i in range(1, len(f)):
        if f[i]:
            res = poly_sum_2(res, poly_step_2(v, i))
            res = reduce_poly_2(res, base, module)
    return res


def calc_poly_field(f, x, base, module):
    res = f[0]
    for i in range(1, len(f)):
        if f[i] != [0]:
            k = poly_mul_2(f[i], poly_step_2(x, i))
            k = reduce_poly_2(k, base, module)
            res = poly_sum_2(res, k)
    return res


def poly_inc(d):
    i = 0
    while i < len(d) and d[i] == 1:
        i += 1
    if i == len(d):
        return [0] * len(d) + [1]
    if d[i] == 0:
        return [0] * i + [1] + d[(i + 1):]


def factor_2_default(n):
    res = list()
    if n == 1:
        return [[1, 1]]
    f = [1] + [0] * (n - 1) + [1]
    d = [0] + [1]
    while f != [1]:
        q, r = poly_div_2(f, d)
        if r == [0]:
            res.append(d)
            f = q
        d = poly_inc(d)
    return res


def reduce_poly_2(f, base, module):
    res = list(f)
    step = len(base) - 1
    swap = base[:step]
    for i in range(len(res) - step):
        if res[step + i] == 1:
            res[step + i] = 0
            res_step = (step + i) % module
            if res_step < len(base) - 1:
                k = [0] * res_step + [1]
                res = poly_sum_2(res, k)
            else:
                st = res_step // step
                num = res_step % step
                k = [0] * num + [1]
                koef = swap
                for j in range(st - 1):
                    koef = poly_mul_2(koef, swap)
                s = reduce_poly_2(poly_mul_2(koef, k), base, module)
                res = poly_sum_2(res, s)
    return res


def poly_mult_param(multipliers, base, module):
    l = len(multipliers)
    res = [1] + [0] * (l - 1) + [1]
    for i in range(l - 1, 0, -1):
        combos = list(combinations(multipliers, i))
        koef = [0]
        for elem in combos:
            alpha_step = sum(k for k in elem) % module
            add = reduce_poly_2([0] * alpha_step + [1], base, module)
            koef = poly_sum_2(zero_poly(koef), add)
            koef = reduce_poly_2(koef, base, module)
        if koef not in [[0], [1]]:
            exit("Fatal mult param.")
        else:
            res[l - i] = koef[0]
    return res


def poly_lcm(polies):
    if len(polies) == 1:
        return polies[0]
    poly_gcd = polies[0]
    for i in range(1, len(polies)):
        poly_gcd = poly_euclid_2(poly_gcd, polies[i])
    poly_mul = polies[0]
    for i in range(1, len(polies)):
        poly_mul = poly_mul_2(poly_mul, polies[i])
    res, r = poly_div_2(poly_mul, poly_gcd)
    if r != [0]:
        exit("Fatal lcm.")
    return res


def poly_to_vec(f, m):
    return f + [0] * (m - len(f))


def poly_reverse(f, base, module):
    if len(f) >= len(base):
        f = reduce_poly_2(f, base, module)
    a = f
    b = base
    res = [1]
    prev = [0]
    while a != [1]:
        q, r = poly_div_2(b, a)
        temp = res
        res = poly_sum_2(poly_mul_2(res, q), prev)
        prev = temp
        a_1 = r
        b = a
        a = a_1
    return res


def zero_poly_field(f):
    while f and f[-1] == [0]:
        f.pop()
    if not f:
        return [[0]]
    return f


def poly_sum_field(f, g):
    if f == [[0]]:
        return g
    if g == [[0]]:
        return f
    if len(g) > len(f):
        return poly_sum_field(g, f)
    m = len(f) - 1
    h = len(g) - 1
    q = [[0] for i in range(m + 1)]
    for i in range(h + 1):
        q[i] = poly_sum_2(f[i], g[i])
    for i in range(h + 1, m + 1):
        q[i] = f[i]
    return zero_poly_field(q)


def poly_mul_field(f, g, base, module):
    m = len(f) - 1
    h = len(g) - 1
    q = [[0] for i in range(m + h + 1)]
    for i in range(h + 1):
        for j in range(m + 1):
            q[i + j] = list(poly_sum_2(q[i + j], reduce_poly_2(poly_mul_2(g[i], f[j]), base, module)))
    return zero_poly_field(q)
