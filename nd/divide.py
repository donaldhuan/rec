#! /usr/bin/python
'''
This script targets at dividing the source data into 2 groups, 
one is for training while the other is for testing. Configurations
are stored in module config.
In fact, it is a random selector of testing data with given rate.
'''
from config import RATING_NUM, TRAIN_RATE
from random import random
from algorithm import _genstr
import sqlite3

conn = sqlite3.connect('../recexpr.db')

trainlst = range(1, RATING_NUM + 1)
testlst = []

TEST_SET_UP = RATING_NUM * (1 - TRAIN_RATE)
while len(testlst) < TEST_SET_UP:
    testlst.append(trainlst.pop(int(random() * len(trainlst))))

conn.execute('DELETE FROM core_train')
conn.execute('INSERT INTO core_train SELECT * FROM core_rating WHERE id IN %s' % _genstr(trainlst))
conn.execute('DELETE FROM core_test')
conn.execute('INSERT INTO core_test SELECT * FROM core_rating WHERE id IN %s' % _genstr(testlst))
conn.commit()
