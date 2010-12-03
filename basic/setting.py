import sqlite3
# database location
conn = sqlite3.connect('../recexpr.db')

# training table name
RATING_TABLE = 'core_train'

# the number of neighbours in KNN
N_NEIGHBOURS = 37

# the number of users in database
N_USERS = 943
