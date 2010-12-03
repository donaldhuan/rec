from config import USER_NUM
from algorithm import sim
import sqlite3
conn = sqlite3.Connection('../recexpr.db')

for i in range(578, USER_NUM + 1):
    for j in range(i + 1, USER_NUM + 1):
        conn.execute('INSERT INTO core_similarity VALUES(%d, %f)' % (i * 1000 + j, sim(i, j)))
        conn.commit()
        print i, j
