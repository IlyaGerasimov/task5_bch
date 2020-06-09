import calc
import poly


def check_f(f, phrase, skip=True, is_float=False):
    if f.readline().strip('\n') != phrase:
        exit("Wrong format.")
    try:
        if is_float:
            res = float(f.readline().strip('\n'))
        else:
            res = int(f.readline().strip('\n'))
    except Exception:
        exit("Wrong format.")
    else:
        if not skip:
            return res


def get_h(f, k):
    res = [0 for i in range(k)]
    if f.readline().strip('\n') != "H:":
        exit("Wrong format.")
    for i in range(k):
        s = f.readline().strip('\n').split(' ')
        res[i] = [int(elem) for elem in s]
    return res


def get_poly(f, phrase):
    if f.readline().strip('\n') != phrase:
        exit("Wrong format.")
    s = f.readline().strip('\n')
    return calc.str_list(s)


def get_info_decode(f):
    t = check_f(f, "t:", skip=False)
    n = check_f(f, "n:", skip=False)
    k = check_f(f, "k:", skip=False)
    check_f(f, "probability of the error in channel:", is_float=True)
    alpha_poly = get_poly(f, "alpha polynomial:")
    b = check_f(f, "b:", skip=False)
    poly_g = get_poly(f, "g polynomial:")
    f.close()
    return n, k, b, t, alpha_poly, poly_g


def get_syndrome(y, b, s, t, module, base):
    syndrome = [0 for i in range(t * 2)]
    for i in range(b, b + t * 2):
        alpha = [0] * (s * i) + [1]
        syndrome[i - b] = poly.calc_poly(y, alpha, base, module)
    return syndrome


def berlekamp_massey(syndrome, t, base, module):
    c_x = list([[1]])
    b_x = list([[1]])
    l = 0
    m = 1
    b = list([1])
    for j in range(2 * t):
        if l >= 1:
            add = [0]
            for i in range(1, l + 1):
                if len(c_x) <= i:
                    continue
                a = list(poly.poly_mul_2(c_x[i], syndrome[j - i]))
                a = list(poly.reduce_poly_2(a, base, module))
                add = list(poly.poly_sum_2(add, a))
            d = list(poly.poly_sum_2(syndrome[j], add))
        else:
            d = list(syndrome[j])
        if d == [0]:
            m = m + 1
        else:
            t_x = list(c_x)
            b_r = list(poly.poly_reverse(b, base, module))
            b_r = list(poly.reduce_poly_2(poly.poly_mul_2(d, b_r), base, module))
            add_x = list([[0] for i in range(m)])
            add_x.append(b_r)
            sub = list(poly.poly_mul_field(add_x, b_x, base, module))
            c_x = list(poly.poly_sum_field(c_x, sub))
            if 2 * l <= j:
                l = j + 1
                b_x = list(t_x)
                b = list(d)
                m = 1
            else:
                m = m + 1
    return l, c_x


def root(c_x, base, s, module):
    n_root = len(c_x) - 1
    roots = dict()
    alpha = [0, 1]
    x = [1]
    i = 0
    j = 0
    while i < module and n_root - j > 0:
        res = poly.calc_poly_field(c_x, x, base, module)
        if res == [0]:
            index = ((- i + module) % module) // s
            roots[index] = x
            j += 1
        i += 1
        x = poly.reduce_poly_2(poly.poly_mul_2(x, alpha), base, module)
    return roots


def final_decode(res_code, poly_g, k, pad):
    s = list()
    b = bytes()
    for code in res_code:
        m, r = poly.poly_div_2(code, poly_g)
        m = m + [0] * (k - len(m))
        print(
            "Decode result for vector {}: {} -> {}".format(
                calc.list_str(code), calc.list_str(code), calc.list_str(m)
            )
        )
        s = s + m
        while len(s) >= 8 and len(s) > pad:
            process = s[:8]
            s = s[8:]
            b = b + calc.list_bytes(process)
    if len(s) != pad:
        exit("Fatal decode.")
    print("Byte representation:")
    print(b)
    try:
        res = b.decode("utf-8")
        print("UTF-8 representation:")
        print(res)
        return res
    except UnicodeDecodeError:
        print("Cannot represent the possible result in UTF-8.")
        return b


def decode_process(g, b, s, t, module, base, n, poly_g, k):
    res_code = list()
    for line in g:
        if 'pad:' in line:
            pad = int(line.strip("\n").strip("pad: "))
            continue
        y = line.strip('\n')
        print("\nRemoving error from", y)
        y = calc.str_list(line.strip('\n'))
        syndrome = get_syndrome(y, b, s, t, module, base)
        l, c_x = berlekamp_massey(syndrome, t, base, module)
        roots = root(c_x, base, s, module)
        e = [1 if i in roots else 0 for i in range(n)]
        for key in roots:
            y[key] = y[key] ^ 1
        print("Calculated error is", calc.list_str(e))
        print("The result code vector is", calc.list_str(y))
        fix_syndrome = get_syndrome(y, b, s, t, module, base)
        unfix_flag = False
        for elem in fix_syndrome:
            if elem != [0]:
                unfix_flag = True
                break
        res_code.append(y)
        if unfix_flag:
            print("The code still has errors.                Failure")
        else:
            print("Achieved the possible result.             Success")
    g.close()
    final_decode(res_code, poly_g, k, pad)


def decode(f, g):
    print("\n Getting decode parameters:")
    n, k, b, t, alpha_poly, poly_g = get_info_decode(f)
    m, module = calc.min_m(2, n)
    s = module // n
    print("\nDone.")
    print("\nStarting decode.")
    decode_process(g, b, s, t, module, alpha_poly, n, poly_g, k)
    print("\nDone.")


# decode(open("./codes/decode0", "r"), open("./code_results/code_result0", "r"))

