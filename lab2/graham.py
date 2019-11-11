from definitions import *

red = '#a03131'
    
def graham_visualization(points, eps=10 ** -14):
    #1. Find point with smallest y, x
    p0 = min(points, key=flip)
    removed = [] # for visualzation purpose

    #2. Sort remaining points
    def partition(points):
        pivot, *tail = points
        low, hihg = [], []
        ret_pivot = pivot
        for p in tail:
            d = det(p0, pivot, p)
            if abs(d) < eps:
                # inline
                if dist_sq(p0, p) > dist_sq(p0, ret_pivot):
                    removed.append(ret_pivot)
                    ret_pivot = p
                else:
                    removed.append(p)
            elif d > 0:
                hihg.append(p)
            else:
                low.append(p)
        return low, hihg, ret_pivot



    def quick_sort(points):
        if len(points) <= 1:
            return points
        low, hihg, pivot = partition(points)
        return quick_sort(low) + [pivot] + quick_sort(hihg)

    #3. Initialize stack
    p1, p2, *tail = quick_sort(points)
    stack = [p0, p1, p2]

    yield Scene([
            PointsCollection(removed, red),
            PointsCollection([p1, p2] + tail, 'gray'),
            PointsCollection([p0], 'green')
    ], [])

    #4. Execute the algorithm
    m = len(tail)
    i = 0
    while i < m:
        yield Scene([
            PointsCollection(removed, red), #removed during sorting
            PointsCollection(tail[:i], '#1f1f1f'), #processed
            PointsCollection([p1, p2] + tail[i:], 'gray'), #not processed
            PointsCollection(stack, 'purple'), #currently on statck
            PointsCollection([p0], 'green') #p0
        ], [ LinesCollection(genLines(stack), 'blue') ])
        pi = tail[i]
        if det(stack[-2], stack[-1], pi) > eps:
            stack.append(pi)
            i += 1
        else:
            stack.pop()

    yield Scene([
        PointsCollection(points, 'gray'),
        PointsCollection(stack, 'green'),
    ], [ LinesCollection(genLines(stack), 'blue') ])