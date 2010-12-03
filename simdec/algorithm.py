from setting import *
DEBUG = False

def ratby(uid, gid):
    '''ratby returns ratings from user(uid) at movies in given genre(gid)'''
    return conn.execute('SELECT movie_id, rating FROM %s WHERE movie_id IN (SELECT movie_id FROM core_movie_genre WHERE genre_id = ?) AND user_id = ? ORDER BY timestamp ASC' % RATING_TABLE, (gid, uid)).fetchall()

def sim(m1, m2):
    '''similarity between two movies'''
    I = corater(m1, m2)
    if DEBUG:
        print 'coraters : %s' % _genstr(I)
    return cos(*genector(R(m1, I), R(m2, I)))

def cos(u, v):
    assert len(u) == len(v)
    N = len(u)
    S = 0
    for i in range(0, N):
        S += u[i] * v[i]
    from math import sqrt
    return abs(S * 1.0) / sqrt(sum([k ** 2 for k in u]) * sum([k ** 2 for k in v]))

def _R(m, I = None):
    '''real ratings of m by users in I.
    If I is None, I should be all people having rated m'''
    if I is None:
        return dict(conn.execute('SELECT user_id, rating FROM %s WHERE movie_id = ?' % RATING_TABLE, (m, )).fetchall())
    return dict(conn.execute('SELECT user_id, rating FROM %s WHERE movie_id = %d AND user_id IN %s' % (RATING_TABLE, m, _genstr(I))).fetchall())

def R(m, I = None):
    '''rating of m by u - averate rating by u'''
    ratings = _R(m, I)
    if DEBUG:
        print 'before modification:', m, ratings
    avg_ratings = averate(I)
    for k in ratings:
        ratings[k] -= avg_ratings[k]
    if DEBUG:
        print 'after modification:', m, ratings
    return ratings

def genector(a, b):
    '''generate vectors of dict a and b'''
    la = []
    lb = []
    for k in a:
        la.append(a[k])
        lb.append(b[k])
    if DEBUG:
        print la, lb
    return la, lb

def averate(users = None):
    '''average rating of users'''
    if users:
        return dict(conn.execute('SELECT user_id, avg(rating) FROM %s GROUP BY user_id HAVING user_id IN %s' % (RATING_TABLE, _genstr(users))).fetchall())
    else:
        return dict(conn.execute('SELECT user_id, avg(rating) FROM %s GROUP BY user_id' % RATING_TABLE).fetchall())

def corater(m1, m2):
    '''users who both rate m1 and m2'''
    cur = conn.execute('SELECT user_id FROM %s WHERE user_id IN (SELECT user_id FROM %s WHERE movie_id = ?) AND movie_id = ?' % (RATING_TABLE, RATING_TABLE), (m1, m2))
    return [e[0] for e in cur.fetchall()]

def _genstr(lst):
    buf = ['(']
    buf.append(str(lst)[1:-1])
    buf.append(')')
    return ''.join(buf)

def coefficient(points):
    '''points are just like [(1, 32), (2, 24), (3, 54), (4, 65), ...]'''
    try:
        xbar = sum([p[0] for p in points]) * 1.0 / len(points)
        ybar = sum([p[1] for p in points]) * 1.0 / len(points)
        lxy = sum([(p[0] - xbar) * (p[1] - ybar) for p in points])
        lxx = sum([(p[0] - xbar) ** 2 for p in points])
        return lxy * 1.0 / lxx
    except:
        None

def tesdec(uid, gid):
    rs = ratby(uid, gid)
    points = []
    for p in rs:
        points.append((len(points) + 1, p[1]))
    coe = coefficient(points)
    return coe < 0 if coe is not None else None

if __name__ == '__main__':
    print tesdec(1, 1)
