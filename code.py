import os
import calc
import random


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


def get_g(f, k):
    res = [0 for i in range(k)]
    if f.readline().strip('\n') != "G:":
        exit("Wrong format.")
    for i in range(k):
        s = f.readline().strip('\n').split(' ')
        res[i] = [int(elem) for elem in s]
    return res


def get_info(f):
    check_f(f, "t:")
    n = check_f(f, "n:", skip=False)
    k = check_f(f, "k:", skip=False)
    p = check_f(f, "probability of the error in channel:", skip=False, is_float=True)
    g = get_g(f, k)
    f.close()
    return n, k, g, p


def gen_e(n, p):
    e = [0 for i in range(n)]
    for i in range(n):
        point = random.uniform(0.0, 1.0)
        # print(point)
        if point <= p:
            e[i] = 1
    return e


def code_input(data_byte, g, n, k):
    code_res = list()
    s = list()
    for byte in data_byte:
        bs = calc.int_10_2(byte, 8)
        s += bs
        while len(s) >= k:
            m = s[:k]
            s = s[k:]
            x = calc.mult_v_m(m, g, n)
            code_res.append([m, x])
            print("Message coding: {} -> {}".format(calc.list_str(m), calc.list_str(x)))
    if s:
        pad = k - len(s)
        print("Performed padding for coding:", pad)
        s = s + [0] * pad
        m = s[:k]
        x = calc.mult_v_m(m, g, n)
        code_res.append([m, x])
        print("Message coding: {} -> {}".format(calc.list_str(m), calc.list_str(x)))
    else:
        pad = 0
    return code_res, pad


def code_error_write(f, code_res, n, p, pad):
    s = ""
    for elem in code_res:
        e = gen_e(n, p)
        y = calc.xor_list(elem[1], e)
        print(
            "Final coding result for message {}: {} xor {} = {}".format(
                calc.list_str(elem[0]), calc.list_str(elem[1]), calc.list_str(e), calc.list_str(y)
            )
        )
        s += calc.list_str(y) + "\n"
    s += "pad: {}".format(pad)
    f.write(s.strip("\n"))


def code(f):
    print("\nLoading info..")
    n, k, g, p = get_info(f)
    print("\nDone.")
    data = input("\nPlease specify your text: ")
    data_byte = str.encode(data, encoding='utf-8')
    # print(data_byte)
    print("\nPerforming encoding..")
    code_res, pad = code_input(data_byte, g, n, k)
    print("\n Done.")
    index = sum([len(files) for r, d, files in os.walk("./code_results")])
    path = "./code_results/code_result{}".format(index)
    print("\nGenerating error vectors and writing the result")
    with open(path, "w") as wf:
        code_error_write(wf, code_res, n, p, pad)
    print("\nDone.")
    print("\nCode result has been written in {}".format(path))


# code(open("./codes/code0", "r"))