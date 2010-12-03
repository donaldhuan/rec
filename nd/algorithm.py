import sqlite3
conn = sqlite3.Connection('../recexpr.db')
DEBUG = False

def sim(u, v):
    if u == v:
        return 1
    elif u > v:
        u, v = v, u
    return conn.execute('SELECT similarity FROM core_similarity WHERE id = %d' % (u * 1000 + v,)).fetchone()[0]

    I = corate(u, v)
    Ru = averate(u, I)
    Rv = averate(v, I)
    a = 0
    b = 0
    c = 0
    cu = conn.execute('select movie_id, rating from core_train where user_id = %d and movie_id in %s' % (u, _genstr(I)))
    rsu = cu.fetchall()
    rsu.sort()
    cv = conn.execute('select movie_id, rating from core_train where user_id = %d and movie_id in %s' % (v, _genstr(I)))
    rsv = cv.fetchall()
    rsv.sort()
    for i in range(0, len(rsu)):
        a += (rsu[i][1] - Ru) * (rsv[i][1] - Rv)
        b += (rsu[i][1] - Ru) ** 2
        c += (rsv[i][1] - Rv) ** 2
    from math import sqrt
    if b * c == 0:
        return 0
    return a / sqrt(b * c)

def corate(u, v):
    c = conn.execute('select movie_id from core_train where user_id = %d and movie_id in (select movie_id from core_train where user_id = %d)' % (u, v))
    return [k[0] for k in c]

def averate(u, I = None):
    if I is None:
        return conn.execute('select avg(rating) from core_train where user_id = %d' % u).fetchone()[0]
    try:
        return conn.execute('select avg(rating) from core_train where user_id = %d and movie_id in %s' % (u, _genstr(I))).fetchone()[0]
    except:
        print u
        print I
        print _genstr(I)

def guess(u, i):
    P = 0
    Ru = averate(u)
    a = 0
    b = 0
    cursor = conn.execute('select user_id, rating from core_train where movie_id = %d' % i)
    rs = cursor.fetchall()
    for c in range(0, len(rs)):
        if DEBUG:
            print '%d / %d' % (c, len(rs))
        if u != rs[c][0]:
            s = sim(u, rs[c][0])
            a += s * (rs[c][1] - averate(rs[c][0]))
            b += abs(s)
    try:
        return a * 1.0 / b + Ru
    except:
        return None

def _genstr(lst):
    '''lst  [1, 2, 3]
    return  '(1, 2, 3)'
    '''
    buf = ['(']
    buf.append(str(lst)[1:-1])
    buf.append(')')
    return ''.join(buf)

if __name__ == '__main__':
    from datetime import datetime
    t = datetime.now()
    print guess(1, 1)
    print datetime.now() - t
