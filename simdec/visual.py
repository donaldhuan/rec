from algorithm import ratby
from pylab import *

figure(0)
scores = [e[1] for e in ratby(1, 10)]
plot(range(1, len(scores) + 1), scores, '.-')
show()
