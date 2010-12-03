GROUP_NUM = 10
NUM_MIN = 5
INF = 9999

def init_group(data):
    result = []
    bound = max(data)
    base = min(data)
    d = (bound - base) * 1.0 / GROUP_NUM
    for i in range(0, GROUP_NUM):
        result.append([0, [base + i * d, base + (i + 1) * d]])
    for i in data:
        if i == bound:
            result[-1][0] += 1
        else:
            ind = int((i - base) / d)
            result[ind][0] += 1
    return result

def merge(lst, i):
    j = i + 1 if i < len(lst) - 1 else i - 1
    if j < i:
        i, j = j, i
    lst[i] = [lst[i][0] + lst[j][0], [lst[i][1][0], lst[j][1][1]]]
    lst.pop(j)

def check(lst):
    for i in range(0, len(lst)):
        if lst[i][0] < NUM_MIN:
            return i
    return None

def group(data):
    result = init_group(data)
    p = check(result)
    while p is not None:
        merge(result, p)
        p = check(result)
    return result

def phat(bound, up, A = 0, V = 1):
    from scipy.stats import norm
    from math import sqrt
    a = (bound - A) * 1.0 / sqrt(V)
    b = (up - A) * 1.0 / sqrt(V)
    if bound == -INF:
        return norm.cdf(b)
    elif up == INF:
        return 1 - norm.cdf(a)
    return norm.cdf(b) - norm.cdf(a)

def chi2test(data):
    from scipy.stats import norm, chi2
    from numpy import var, average
    A = average(data)
    V = var(data)
    N = len(data)
    grplst = group(data)
    grplst[0][1][0] = -INF
    grplst[-1][1][1] = INF
    X2 = 0
    for k in grplst:
        np = N * phat(k[1][0], k[1][1], A, V)
        X2 += k[0] ** 2 / np
    X2 -= N
    return chi2(len(grplst) - 3).cdf(X2)

def load(ind):
    f = open('result/result_%s' % str(ind))
    import pickle
    data = pickle.load(f)
    f.close()
    return data

if __name__ == '__main__':
    s = 0
    for i in range(1, 944):
        if chi2test(load(i)) < 0.95:
            s += 1
    print s * 1.0 / 944
