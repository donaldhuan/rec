import sqlite3
from algorithm import guess
from numpy import average
from config import USER_NUM
from ndtest import chi2test, load

conn = sqlite3.Connection('recexpr.db')
cache = {}
for i in range(1, USER_NUM + 1):
    f = open('result/result_%d' % i)
    import pickle
    cache[i] = pickle.load(f)
    f.close()

def mae(func):
    std = conn.execute('SELECT user_id, movie_id, rating FROM core_test').fetchall()
    N = len(std)
    s = 0
    i = 0
    for k in std:
        pr = func(k[0], k[1])
        if pr:
            print i, N
            s += abs(k[2] - pr)
            i += 1
        else:
            print 'a None occurs'
            N -= 1
    return s / N

def modified(func):
    def foo(uid, mid):
        orisult = func(uid, mid)
        if orisult:
            if chi2test(load(uid)) < 0.95:
                return orisult - average(cache[i])
            else:
                return orisult
        else:
            return None
    return foo

if __name__ == '__main__':
    print mae(modified(guess))
