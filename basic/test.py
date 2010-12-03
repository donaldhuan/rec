import unittest
from random import random
import algorithm_hjw
import algorithm
N_USER = 943
N_MOVIE = 1682

class SimTester(unittest.TestCase):
    def testMain(self):
        for i in range(0, 1000):
            u = int(random() * N_USER + 1)
            v = int(random() * N_USER + 1)
            self.assertTrue(abs(algorithm.sim(u, v) - algorithm_hjw.sim(u, v)) < 0.01)

class GuessTester(unittest.TestCase):
    def testMain(self):
        for i in range(0, 1000):
            u = int(random() * N_USER + 1)
            m = int(random() * N_MOVIE + 1)
            self.assertTrue(abs(algorithm.guess(u, m) - algorithm_hjw.guess(u, m)) < 0.01, msg = (u, m))

if __name__ == '__main__':
    unittest.main()
