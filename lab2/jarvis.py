from definitions import *

def jarvis_visualization(points, eps = 10 ** -14):
    size = len(points)
    def swap(i, j):
        points[i], points[j] = points[j], points[i]

    p1, i = min_index(points, key=flip), 1
    swap(0, p1)

    while True:
        m = i
        for j in range(i + 1, size + 1):
            j %= size
            p = points[j]
            d = det(points[i - 1], points[m], p)
            if abs(d) < eps and dist_sq(points[i - 1], p) > dist_sq(points[i - 1], points[m]) or d < 0:
                m = j

        yield Scene([
                PointsCollection(points[i:], 'gray'),
                PointsCollection(points[:i], 'green')
        ], [ LinesCollection(genLines(points[:i]), 'blue') ])
        if m == 0:
            break
        swap(i, m)
        i += 1

    return points[:i]