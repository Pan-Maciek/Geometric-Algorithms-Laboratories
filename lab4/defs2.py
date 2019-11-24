from math import ceil
from enum import Enum
from collections import deque
from definitions import *

def iter_3(values):
    it = iter(values)
    a, b = next(it), next(it)
    v0, v1 = a, b
    for c in it:
        yield a, b, c
        a, b = b, c
    yield (a, b, v0)
    yield (b, v0, v1)

INLINE = COLL = 0
LEFT = CCW = 1
RIGHT = CW = -1

def det(a, b, c):
    (ax, ay) = a
    (bx, by) = b
    (cx, cy) = c
    return (ax - cx) * (by - cy) - (ay - cy) * (bx - cx)

def orientation(a, b, c, det=det, eps=10**-12):
    d = det(a, b, c)
    if abs(d) < eps:
        return COLL
    return CCW if d > 0 else CW

class VertType(Enum):
    start = 'green'
    end = 'red'
    join = 'blue'
    split = 'lightblue'
    regular = 'brown'

def classify_point(a, b, c):
    # classifying point b
    orient = orientation(a, b, c)
    _, ay = a
    _, by = b
    _, cy = c
    
    if ay < by and cy < by: # początkowy, dzielący
        if orient == LEFT: return VertType.start
        elif orient == RIGHT: return VertType.split
        else: return VertType.regular
    elif ay > by and cy > by: # końcowy, łączący
        if orient == LEFT: return VertType.end
        elif orient == RIGHT: return VertType.join
        else: return VertType.regular
    else: return VertType.regular


def is_y_mon(poly):
    return not any(vert_type in (VertType.split, VertType.join) 
        for vert_type in (classify_point(a, b, c) for a, b, c in iter_3(poly)))

def find_extrems(poly, ax=1):
    min_val = max_val = poly[0][ax]
    min_index = max_index = 0
    for i, point in enumerate(poly):
        y = point[ax]
        if y < min_val:
            min_index = i
            min_val = y
        elif y > max_val:
            max_index = i
            max_val = y 
    return min_index, max_index

def find_chain(start, end, size):
    chain = set()
    while start != end:
        chain.add(start)
        start = (start + 1) % size
    return chain

def find_chains(poly, ax=1):
    min_index, max_index = find_extrems(poly, ax)
    size = len(poly)
    left_chain, right_chain = find_chain(max_index, min_index, size), find_chain(min_index, max_index, size)

    return left_chain, right_chain

def tr_to_line_col(poly, triangles, **kwargs):
    s = set()
    for a, b, c in triangles:
        s.add((poly[a], poly[b]))
        s.add((poly[a], poly[c]))
        s.add((poly[b], poly[c]))
    return LinesCollection(list(s), **kwargs)

def triangulate_vis(poly, plot):
    ax = 1
    left_chain, right_chain = find_chains(poly, ax)

    size = len(poly)
    vertices = list(sorted(range(size), key=lambda x: poly[x][ax], reverse=True))

    v0, v1, *vertices = vertices
    stack, triangles = deque([v0, v1]), []

    def connect_all(v):
        while len(stack) > 1:
            triangles.append((stack[0], stack[1], v))
            stack.popleft()
        stack.append(v)
    
    def connect_if(v, orient):
        top = stack.pop()
        while stack and orientation(poly[top], poly[v], poly[stack[-1]]) == orient:
            triangles.append((top, v, stack[-1]))
            top = stack.pop()
        stack.extend([top, v])

    for vert in vertices:
        top = stack[-1]
        yield Scene([ 
            PointsCollection([poly[i] for i in stack], color='green'),
            PointsCollection([poly[stack[-1]]], color='blue'),
            PointsCollection([poly[vert]], color='red')
        ], [
            LinesCollection(plot.get_added_figure()[0].lines, color='gray'),
            tr_to_line_col(poly, triangles)
        ])
        if top in left_chain and vert in left_chain:
            connect_if(vert, LEFT)
        elif top in right_chain and vert in right_chain:
            connect_if(vert, RIGHT)
        else:
            connect_all(vert)
    
    yield Scene([ ], [
        LinesCollection(plot.get_added_figure()[0].lines, color='gray'),
        tr_to_line_col(poly, triangles)
    ])