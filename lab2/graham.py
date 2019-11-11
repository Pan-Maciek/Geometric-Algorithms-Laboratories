from definitions import *

def graham_visualization(points, eps=10**-12, det=det):
    #1. Find point with smallest y, x
    p0 = min(points, key=flip)
    allP = PointsCollection(points, 'gray')

    #2. Sort remaining points
    def partition(points):
        pivot, *tail = points
        low, high = [], []
        ret_pivot = pivot
        for p in tail:
            d = orientation(p0, pivot, p, det, eps)
            if d == INLINE:
                if dist_sq(p0, p) > dist_sq(p0, ret_pivot):
                    ret_pivot = p
            elif d == CCW: high.append(p)
            else: low.append(p)
        return low, ret_pivot, high

    def quick_sort(points):
        if len(points) <= 1: return points
        low, pivot, high = partition(points)
        return quick_sort(low) + [pivot] + quick_sort(high)

    #3. Initialize stack
    p1, p2, *tail = quick_sort(points)
    stack = [p0, p1, p2]

    # 4. Execute the algorithm
    i, m = 0, len(tail)
    while i < m:
        pi = tail[i]
        yield Scene([
            allP,
            PointsCollection(stack, 'green'),
        ], [ 
            LinesCollection(genLines(stack), 'blue'),
            LinesCollection([[stack[-1], pi]], 'red')
        ])
        if det(stack[-2], stack[-1], pi) > eps:
            stack.append(pi)
            i += 1
        else: stack.pop()

    yield Scene([ allP, PointsCollection(stack, 'green'), ], [
         LinesCollection(genLines(stack) + [[stack[-1], p0]], 'blue') 
    ])
