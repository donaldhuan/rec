from algorithm import guess
from config import USER_NUM
import sqlite3
conn = sqlite3.Connection('../recexpr.db')

def get_errors(uid):
    result = []
    pdb = conn.execute('SELECT movie_id, rating FROM core_train WHERE user_id = %d' % uid).fetchall()
    for entry in pdb:
        try:
            e = guess(uid, entry[0]) - entry[1]
            result.append(e)
        except:
            pass
    return result

def check():
    for i in range(1, USER_NUM + 1):
        try:
            open('result/result_%d' % i)
        except:
            return i

if __name__ == '__main__':
    import pickle
    start = check()
    for i in range(start, USER_NUM + 1):
        print '%d/%d' % (i, USER_NUM)
        errs = get_errors(i)
        f = open('result/result_%d' % i, 'w')
        pickle.dump(errs, f)
        f.close()

