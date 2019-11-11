from definitions import *

def jarvis_visualization(points, eps=10**-12, det=det2):
    p = [min(points)]

    allP = PointsCollection(points, 'gray')
    while True:
        m = points[0]
        for q in points:
            yield Scene([ allP, PointsCollection(p, 'green') ], [
                LinesCollection(genLines(p), 'blue'),
                LinesCollection([[p[-1], m]], 'green'),
                LinesCollection([[p[-1], q]], 'red')
            ])
            o = orientation(p[-1], m, q, det=det, eps=eps)
            if m == p[-1] or o == RIGHT:
                m = q
            elif o == INLINE:
                if dist_sq(p[-1], m) < dist_sq(p[-1], q):
                    m = q
        if m == p[0]:
            break
        p.append(m)
    yield Scene([ allP, PointsCollection(p, 'green')], [ LinesCollection(genLines(p) + [[p[-1], p[0]]], 'blue') ])
    return p