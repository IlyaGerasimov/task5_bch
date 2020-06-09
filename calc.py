def pow(x, y, n=None):
    if n:
        if y == 0:
            return 1
        if y == 1:
            return x % n
        res = 1
        while y:
            if y & 1 == 1:
                res = res * x % n
            x = x * x % n
            y = y // 2
    else:
        if y == 0:
            return 1
        if y == 1:
            return x
        res = 1
        while y:
            if y & 1 == 1:
                res = res * x
            x = x * x
            y = y // 2
    return res


def min_m(p, n):
    m = 1
    res = pow(p, m) - 1
    while res % n != 0:
        m += 1
        res = pow(p, m) - 1
    return m, res


def cycle_set(p, n, step=1):
    res = dict()
    elems = [i for i in range(step, n, step)]
    while elems:
        base = elems[0]
        l = [base]
        elems.remove(base)
        next_elem = p * base % n
        while next_elem != base:
            l.append(next_elem)
            elems.remove(next_elem)
            next_elem = p * next_elem % n
        res[base] = l
    return res


def mult_v_m(v, m, l):
    r = len(v)
    res = [0 for i in range(l)]
    for i in range(l):
        elem = False
        for j in range(len(v)):
            elem ^= v[j] & m[j][i]
        res[i] = elem
    return res


def mult_m_v(m, v):
    r = len(v)
    res = [0 for i in range(len(m))]
    for i in range(len(m)):
        elem = False
        for j in range(r):
            elem ^= v[j] & m[i][j]
        res[i] = elem
    return res


def int_bool(n, r):
    return [bool(n & (1 << j)) for j in range(r - 1, -1, -1)]


def bool_int(b):
    n = 0
    for elem in b:
        n = n << 1
        if elem:
            n += int(elem)
    return n


def int_10_2(n, l):
    return [int(bool(n & (1 << j))) for j in range(l - 1, -1, -1)]


def list_str(v):
    s = ""
    for elem in v:
        s = s + str(elem)
    return s


def list_bytes(v):
    s = list_str(v)
    return int(s, 2).to_bytes(len(s) // 8, byteorder='big')


def str_list(s):
    return [int(elem) for elem in s]


def xor_list(a, b):
    if len(a) != len(b):
        exit("Fatal xor for lists.")
    return [a[i] ^ b[i] for i in range(len(a))]
