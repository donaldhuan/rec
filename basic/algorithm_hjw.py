from setting import *
DEBUG = False 

#compute the mode of the ratings that a user gave
def mode(u):
    rs = conn.execute('SELECT COUNT(rating), rating FROM %s WHERE user_id = %d GROUP BY rating' % (RATING_TABLE, u)).fetchall()
    return max(rs)[1]
    mode = [0, 0, 0, 0, 0]
    ur = conn.execute('select rating from %s where user_id = %d' % (RATING_TABLE, u))
    ur = ur.fetchall()
    mmax = 0
    for i in range(0, len(ur)):
        mode[ur[i][0] - 1] += 1
    # print mode
    mmax = max(mode)
    mmode = []
    for i in range(0, 5):
        if mode[i] == mmax:
            mmode.append(i + 1)
    if len(mmode) != 1:
        return 3
    return mmode[0]



#according to the mode to compute the similarity of two users
def sim_mode(u, v):
    I = corate(u, v)
    Ru = mode(u)
    Rv = mode(v)
    a = 0
    b = 0
    c = 0
    cu = conn.execute('select movie_id, rating from %s where user_id = %d and movie_id in %s' % (RATING_TABLE, u, _genstr(I)))
    rsu = cu.fetchall()
    rsu.sort()
    cv = conn.execute('select movie_id, rating from %s where user_id = %d and movie_id in %s' % (RATING_TABLE, v, _genstr(I)))
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

def sim(u, v):
    I = corate(u, v)
    Ru = averate(u, I)
    Rv = averate(v, I)
    a = 0
    b = 0
    c = 0
    cu = conn.execute('select movie_id, rating from %s where user_id = %d and movie_id in %s' % (RATING_TABLE, u, _genstr(I)))
    rsu = cu.fetchall()
    rsu.sort()
    cv = conn.execute('select movie_id, rating from %s where user_id = %d and movie_id in %s' % (RATING_TABLE, v, _genstr(I)))
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

# Do not fetch only one row in a complete statement, which will slow down computing speed.
'''
def R(u, i):
    c = conn.execute('select rating from %s where user_id = %d and movie_id = %d' % (RATING_TABLE, u, i))
    return c.fetchone()[0]
'''

def corate(u, v):
    c = conn.execute('select movie_id from %s where user_id = %d and movie_id in (select movie_id from %s where user_id = %d)' % (RATING_TABLE, u, RATING_TABLE, v))
    return [k[0] for k in c]

def averate(u, I = None):
    if I is None:
        return conn.execute('select avg(rating) from %s where user_id = %d' % (RATING_TABLE, u)).fetchone()[0]
    return conn.execute('select avg(rating) from %s where user_id = %d and movie_id in %s' % (RATING_TABLE, u, _genstr(I))).fetchone()[0]

def create_cache():
    # print 'b'
    from sys import exit
    us = conn.execute('select id from core_user')
    us = us.fetchall()
    us.sort()
    us = [k[0] for k in us]
    flag = conn.execute('select max(id) from core_similarity').fetchone()[0]
    if flag is None:
        flag = 0
    for u in us:
        for v in us:
            id = u * 1000 + v
            if id > flag:
                if u == v:
                    s = 1
                else:
                    s = sim(u, v)
                conn.execute('insert into core_similarity(id, similarity) values(%d, %f)' % (id, s))
                conn.commit()
                # print u, v

def convert(string):
    return (4 - len(string)) * '0' + string

def create_cache_two():
    ur = conn.execute('select id from core_user')
    ur = ur.fetchall()
    ur = [k[0] for k in ur]
    for c in ur:
        um = conn.execute('select id from core_movie where id not in (select movie_id from %s where user_id = %d)' % (RATING_TABLE, c))
        um = um.fetchall()
        um = [k[0] for k in um]
        mm = []
        print c
        for m in um:
            mm.append((guess(c, m), m))
        mm.sort(reverse = True)
        forecast = convert(str(mm[0][1])) + convert(str(mm[1][1])) + convert(str(mm[2][1])) + convert(str(mm[3][1])) + convert(str(mm[4][1]))
        conn.execute('insert into core_forecast_rating (user_id, foremovie) values (%d, "%s")' % (c, forecast))
        conn.commit()

def guess(u, i):
    P = 0
    Ru = averate(u)
    a = 0
    b = 0
    vs = [k[0] for k in conn.execute('select user_id from %s where movie_id = %d' % (RATING_TABLE, i)).fetchall()]
    cursor = conn.execute('select user_id, rating from %s where movie_id = %d and user_id in %s' % (RATING_TABLE, i, _genstr(vs)))
    rs = cursor.fetchall()
    for c in range(0, len(rs)):
        if DEBUG:
            print '%d / %d' % (c, len(rs))
        if u != rs[c][0]:
            if u == rs[c][0]:
                s = 1
            else:
                d = min(u, rs[c][0])
            #     id = a * 1000 + u + rs[c][0] - a
                id = d * 999 + u +rs[c][0]
                # s = conn.execute('select similarity from core_similarity where id = %d' % id).fetchone()[0]
                s = sim(id / 1000, id % 1000)
            a += s * (rs[c][1] - averate(rs[c][0]))
            b += abs(s)
    try:
        return a * 1.0 / b + Ru
    except:
        Ru

def rrecommend(u):
    string = conn.execute('select foremovie from core_forecast_rating where user_id = %d' % u).fetchone()[0]
    rec = []
    str = [0, 0, 0, 0, 0]
    str[0] = string[:4]
    str[1] = string[4:8]
    str[2] = string[8:12]
    str[3] = string[12:16]
    str[4] = string[16:]
    for i in range(0,5):
        movie = conn.execute('select title from core_movie where id = %d' % int(str[i])).fetchone()[0]
        rec.append(movie)
    return rec

def mae():
    a = 0
    rt = conn.execute('select user_id, movie_id ,rating from %s' % RATING_TABLE)
    rt = rt.fetchall()
    try:
        for c in range(0, len(rt)):
            s = guess(rt[c][0], rt[c][1])
            a += abs(s - rt[c][2])
        return a * 1.0 / len(rt)
    except:
        print rt[c]
    # for c in range(0, len(rt)):
    #     s = guess(rt[c][0], rt[c][1])
    #     a += abs(s - rt[c][2])
    # return a * 1.0 / 100000

def _genstr(lst):
    '''lst  [1, 2, 3]
    return  '(1, 2, 3)'
    '''
    buf = ['(']
    for i in range(0, len(lst)):
        if i != len(lst) - 1:
            buf.append('%d,' % lst[i])
        else:
            buf.append('%d' % lst[i])
    buf.append(')')
    return ''.join(buf)

if __name__ == '__main__':
    print guess(1, 2)
