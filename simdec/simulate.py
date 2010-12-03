from algorithm import ratby

THRESHOLD = 2
DEBUG = False

def clean(points):
    '''clean converts [(342, 3), (243, 5), ...] to [(1, 3), (2, 5)]'''
    ret = []
    for i in range(0, len(points)):
        ret.append((i + 1, points[i][1]))
    return ret

def _test_line(points):
    global THRESHOLD
    if len(points) < 3:
        return True
    k = (points[-1][1] - points[0][1]) * 1.0 / (points[-1][0] - points[0][0])
    if DEBUG:
        print 'y = %f * x + %f' % (k, points[0][1] - k)
    f = lambda x : points[0][1] + k * x - k
    for p in points:
        if abs(p[1] - f(p[0])) > THRESHOLD:
            return False
    return True


def simulate(points):
    if len(points) > 1:
        rsv = [0]
        for i in range(2, len(points)):
            if not _test_line(points[rsv[-1] : i + 1]):
                rsv.append(i - 1)
        rsv.append(len(points) - 1)
        return rsv

if __name__ == '__main__':
    points = clean(ratby(1, 1))
    print points
    choices = simulate(points)
    print choices
    print len(choices) * 1.0 / len(points)
