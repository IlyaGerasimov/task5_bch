import os
from math import log2
import calc
import poly


def get_max_delta(classes, cyclotomic_c, b, module, s):
    index = b
    b_new = b
    flag = True
    while flag and index > s:
        index = index - s
        flag_in = False
        for elem in classes:
            if index in cyclotomic_c[elem]:
                flag_in = True
                break
        if flag_in:
            b_new = index
        else:
            flag = False
    index = b
    flag = True
    length = int((b - b_new) / s) + 1
    while flag and index < module - s - 1:
        index = index + s
        flag_in = False
        for elem in classes:
            if index in cyclotomic_c[elem]:
                flag_in = True
                break
        if flag_in:
            length += 1
        else:
            flag = False
    return int(b_new / s), length


def get_sizes(cyclotomic_c, module, n, step=1):
    res = dict()
    for i in range(2, n):
        alpha = [step + j for j in range(i)]
        while alpha[-1] <= module:
            classes = list()
            for key, value in cyclotomic_c.items():
                for elem in alpha:
                    if elem in value and key not in classes:
                        classes.append(key)
                        break
            key = n - sum(len(cyclotomic_c[elem]) for elem in classes)
            beg, delta_2 = get_max_delta(classes, cyclotomic_c, alpha[0], module, step)
            if key not in res:
                res[key] = [classes, alpha[0], beg, delta_2]
            elif delta_2 > res[key][3]:
                res[key] = [classes, alpha[0], beg, delta_2]
            alpha = [elem + step for elem in alpha]
    return res


'''
def get_t(alphas, cyclotomic_c, step, beg, module):
    if len(alphas) == 1:
        return 1
    cycl = list()
    for i in range(len(alphas)):
        cycl = cycl + cyclotomic_c[alphas[i]]
    elem = beg
    delta = 1
    while elem in cycl and elem < module:
        delta += 1
        elem = elem + step
        print(elem)
    return int((delta - 1) / 2)
'''


def get_params(n, bandwidth):
    if n % 2 == 0:
        n = n - 1
    while n > 0:
        m, module = calc.min_m(2, n)
        s = module // n
        cyclotomic_c = calc.cycle_set(2, module, s)
        print("\n   Getting all possible message length..")
        pos_k = get_sizes(cyclotomic_c, module, n, s)
        print("\n   Done.")
        keys = sorted(pos_k)
        for i in range(len(keys) - 1, -1, -1):
            speed = keys[i] / n
            if speed < bandwidth:
                b = pos_k[keys[i]][2]
                size = pos_k[keys[i]][0]
                t = int((pos_k[keys[i]][3] + 1) / 2)
                return n, m, s, module, speed, keys[i], cyclotomic_c, size, b, t
        n = n - 2
    exit("Cannot build code. Unable to achieve conditions for bandwidth and BCH code")


def get_alpha(polies, n, m, module):
    alpha = [0, 1]
    for elem in polies:
        if len(elem) == m + 1:
            f = [1]
            i = 1
            while i < n:
                f = poly.poly_mul_2(f, alpha)
                tmp = poly.reduce_poly_2(f, elem, module)
                if tmp == [1]:
                    break
                i += 1
            if i == n:
                return elem
    return None


def mapping(cycl, alpha_poly, n, module):
    res = dict({0: [0, 1]})
    for key, value in cycl.items():
        if key == 0:
            res[n] = [1, 1]
        elif key == 1:
            res[1] = alpha_poly
        else:
            res[key] = poly.poly_mult_param(value, alpha_poly, module)
    return res


def get_lcm_polynomials(cyclo_poly, b):
    res = list()
    for i in b:
        res.append(cyclo_poly[i])
    return res


def get_g(poly_g, n, k):
    g = [[0 for i in range(n)] for i in range(k)]
    for i in range(k):
        g[i] = [0] * i + poly_g + [0] * (n - len(poly_g) - i)
    return g


def get_h(size, b, m, n, module, base):
    h = [[0 for i in range(n)] for j in range(len(size) * m)]
    for i in range(len(size)):
        vec = [1]
        step = poly.reduce_poly_2([0] * (b + i) + [1], base, module)
        for j in range(n):
            elem = poly.poly_to_vec(vec, m)
            for k in range(m):
                h[i * m + k][j] = elem[m - 1 - k]
            vec = poly.reduce_poly_2(poly.poly_mul_2(vec, step), base, module)
    return h


def write_g(g, k, n, f):
    for i in range(k):
        s = ""
        for j in range(n):
            s += str(g[i][j]) + " "
        f.write(s.strip(' '))
        f.write("\n")


def write_h(h, n, f):
    for i in range(len(h)):
        s = ""
        for j in range(n):
            s += str(h[i][j]) + " "
        f.write(s.strip(' '))
        f.write("\n")


def write_poly(f, poly_g):
    s = calc.list_str(poly_g)
    f.write(s)


def gen(n, p):
    entropy = -(p * log2(p)) - (1 - p) * log2(1 - p)
    bandwidth = 1 - entropy
    print("\nCalculating parameters..")
    n, m, s, module, speed, k, cyclotomic_c, size, b, t = get_params(n, bandwidth)
    print("Done.")
    print("\nCalculating primitive polynomials..")
    prim_poly = poly.factor_2_default(module)
    print("\nDone.")
    print("\nGetting alpha..")
    alpha_poly = get_alpha(prim_poly, n, m, module)
    print("alpha poly: ", alpha_poly)
    print("\nDone.")
    print("\nMapping cyclotomic classes and polynomials..")
    cyclo_poly = mapping(cyclotomic_c, alpha_poly, n, module)
    print("\nDone.")
    print("\nGetting polynomials for the code polynomial..")
    lcm_polynomials = get_lcm_polynomials(cyclo_poly, size)
    print("\nDone.")
    print("\nGetting code polynomial from the lcm..")
    print(lcm_polynomials)
    poly_g = poly.poly_lcm(lcm_polynomials)
    print("poly_g", poly_g)
    print("poly g", poly_g)
    print("\nDone.")
    print("\nGetting G matrix..")
    g = get_g(poly_g, n, k)
    print("\nDone.")
    print("\nGetting H matrix..")
    h = get_h(size, b, m, n, module, alpha_poly)
    print("\nDone.")
    index = sum([len(files) for r, d, files in os.walk("./codes")])
    path = "./codes/code{}".format(index)
    with open(path, "w") as f:
        f.write("t:\n")
        f.write(str(t))
        f.write("\nn:\n")
        f.write(str(n))
        f.write("\nk:\n")
        f.write(str(k))
        f.write("\nprobability of the error in channel:\n")
        f.write(str(p))
        f.write("\nG:\n")
        write_g(g, k, n, f)
    print("\nFull Code information has been written in {}".format(path))
    path = "./codes/decode{}".format(index)
    with open(path, "w") as f:
        f.write("t:\n")
        f.write(str(t))
        f.write("\nn:\n")
        f.write(str(n))
        f.write("\nk:\n")
        f.write(str(k))
        f.write("\nprobability of the error in channel:\n")
        f.write(str(p))
        f.write("\nalpha polynomial:\n")
        f.write(calc.list_str(alpha_poly))
        f.write("\nb:\n")
        f.write(str(b))
        f.write("\ng polynomial:\n")
        write_poly(f, poly_g)
    print("\nFull Decode information has been written in {}".format(path))


# gen(15, 0.01)
