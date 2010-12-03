from setting import *
from scipy.optimize import fmin
from numpy import array

# Every function whose name starts with '_' is an inner function 
# that are not ought to be called outside.

def sim(u, v):
    '''sim(u, v) returns Pearson Correlation Coefficient ranging from -1 to 1 between u and v'''
    # cache layer
    if u > v:
        u, v = v, u
    try:
        return conn.execute('SELECT similarity FROM core_similarity WHERE id = %d' % (u * 1000 + v)).fetchone()[0]
    except:
        pass
    # compute similarity between two users
    I = corate(u, v)
    try:
        return _cos(get_ratings(u, I), get_ratings(v, I))
    except:
        # exception occurs only when ratings of user are all zeros.
        return 0

def _cos(v1, v2):
    '''returns the cosine value of two vectors v1 and v2'''
    from math import sqrt
    up = 0.0
    for i in range(0, len(v1)):
        up += v1[i] * v2[i]
    return up * 1.0 / sqrt(sum([v ** 2 for v in v1]) * sum([v ** 2 for v in v2]))

def corate(u, v):
    '''returns movie_id(ASC) which is co-rated by both u and v'''
    return [e[0] for e in conn.execute('SELECT movie_id FROM %s WHERE user_id = %d AND movie_id IN (SELECT movie_id FROM %s WHERE user_id = %d) ORDER BY movie_id ASC' % (RATING_TABLE, u, RATING_TABLE, v)).fetchall()]

def get_ratings(u, I):
    '''returns all ratings(ASC by movie_id and ratings are adjusted by _baseline function) rated by u to items in I, which are not allowed to be None'''
    ratings = _get_ratings(u, I)
    _base = _baseline(u, I)
    return [r - _base for r in ratings]

def _get_ratings(u, I):
    '''returns raw ratings(ASC by movie_id) rated by u to items in I, which are not allowed to be None'''
    return [r[1] for r in conn.execute('SELECT movie_id, rating FROM %s WHERE user_id = %d AND movie_id IN %s ORDER BY movie_id ASC' % (RATING_TABLE, u, _genstr(I))).fetchall()]

def _baseline(u, I = None):
    '''used to adjust raw ratings using proper way, i.e. average rating of a given user'''
    if I:
        group = _genstr(I)
        return conn.execute('SELECT AVG(rating) FROM %s WHERE user_id = %d AND movie_id IN %s' % (RATING_TABLE, u, group)).fetchone()[0]
    return conn.execute('SELECT AVG(rating) FROM %s WHERE user_id = %d' % (RATING_TABLE, u)).fetchone()[0]

def _genstr(lst):
    '''lst  [1, 2, 3]
    return  '(1, 2, 3)'
    '''
    buf = ['(']
    buf.append(str(lst)[1:-1])
    buf.append(')')
    return ''.join(buf)

def _guess(user, movie):
    '''traditional guessing method using average baseline'''
    neighbours = conn.execute('SELECT user_id, rating FROM %s WHERE user_id != %d AND movie_id = %d ORDER BY user_id ASC' % (RATING_TABLE, user, movie)).fetchall()
    if not neighbours:
        return _baseline(user)
    simlist = [(sim(user, u[0]), u[0], u[1] - _baseline(u[0])) for u in neighbours] # [sim_value, user_id, score - preference]
    cmp = lambda x, y: 1 if abs(x[0]) > abs(y[0]) else (0 if abs(x[0]) == abs(y[0]) else -1)
    simlist.sort(cmp, reverse = True)
    N = min(len(simlist), N_NEIGHBOURS)
    # N = max(len(simlist), 0)
    _sum = 0
    _sum_sim = 0
    for i in range(0, N):
        _sum += simlist[i][0] * simlist[i][2]
        _sum_sim += abs(simlist[i][0])
    _sum /= _sum_sim
    return _sum + _baseline(user)

def guess(user, movie):
    '''experimental guessing method using linear transformational function'''
    neighbours = conn.execute('SELECT user_id, rating FROM %s WHERE user_id != %d AND movie_id = %d ORDER BY user_id ASC' % (RATING_TABLE, user, movie)).fetchall()
    if not neighbours:
        return _baseline(user)
    simlist = [(sim(user, u[0]), u[0], u[1]) for u in neighbours] # [abs(sim_value), user_id, score]
    cmp = lambda x, y: 1 if abs(x[0]) > abs(y[0]) else (0 if abs(x[0]) == abs(y[0]) else -1)
    simlist.sort(cmp, reverse = True)
    N = min(len(simlist), N_NEIGHBOURS)
    # N = max(len(simlist), 0)
    _sum = 0
    _sum_sim = 0
    for i in range(0, N):
        _sum += abs(simlist[i][0]) * gen_func(simlist[i][1], user)(simlist[i][2])
        _sum_sim += abs(simlist[i][0])
    _sum /= _sum_sim
    return _sum

def cache(init = False):
    '''making the cache layer of similarity'''
    if init:
        conn.execute('DELETE FROM core_similarity')
    for i in range(1, N_USERS + 1):
        for j in range(i, N_USERS + 1):
            try:
                conn.execute('INSERT INTO core_similarity VALUES(%d, %f)' % (i * 1000 + j, sim(i, j)))
                conn.commit()
                print i, j
            except:
                pass

def mae():
    '''calculate the MAE value using guess function'''
    rs = conn.execute('SELECT user_id, movie_id, rating FROM core_test ORDER BY user_id, movie_id ASC').fetchall()
    _mae = 0
    i = 0
    N = len(rs)
    for r in rs:
        try:
            _mae += abs(guess(r[0], r[1]) - r[2])
            i += 1
            if not i % 100:
                print i, N
        except:
            print 'error occurs: %d' % i
            N -= 1
    return _mae * 1.0 / len(rs)

def gen_func(u, v):
    '''R(v) = a + b * R(u)'''
    # cache layer
    try:
        a, b = conn.execute('SELECT a, b FROM core_func WHERE id = %d' % (u * 1000 + v)).fetchone() 
        return lambda x: a + b * x
    except:
        pass
    # unsuccessful hit
    I = corate(u, v)
    ru = _get_ratings(u, I)
    rv = _get_ratings(v, I)
    return _gen_func(ru, rv)

def _gen_func(ru, rv):
    '''[rv] = a + b * [ru]'''
    ru, rv = array(ru), array(rv)
    fp = lambda x, p: p[0] + p[1] * x
    e = lambda p, y, x: abs(fp(x, p) - y).sum()
    p = fmin(e, array([0, 1]), args = (rv, ru), maxiter = 10000, maxfun = 10000, disp = 0)
    return lambda x: fp(x, p)

def cache_func(init = False):
    '''caching function parameters -- a and b in R(v) = a + b * R(u)'''
    if init:
        conn.execute('DELETE FROM core_func')
    for i in range(1, N_USERS + 1):
        for j in range(1, N_USERS + 1):
            try:
                I = corate(i, j)
                ru, rv = array(_get_ratings(i, I)), array(_get_ratings(j, I))
                fp = lambda x, p: p[0] + p[1] * x
                e = lambda p, y, x: abs(fp(x, p) - y).sum()
                p = fmin(e, array([0, 1]), args = (rv, ru), maxiter = 10000, maxfun = 10000, disp = 0)
                a, b = p[0], p[1]
                conn.execute('INSERT INTO core_func VALUES(%d, %lf, %lf)' % (i * 1000 + j, a, b))
            except:
                conn.commit()
        print i
        conn.commit()

if __name__ == '__main__':
    print sim(1, 2)
