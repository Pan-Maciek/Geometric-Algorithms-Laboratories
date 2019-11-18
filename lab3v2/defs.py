from math import fabs

ABOVE, BELOW, EQUAL = 1, -1, 0
START, INTERSECT, END = 3, 4, 5
EPS = 1e-6

def line(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    A = y1 - y2
    B = x2 - x1
    C = x2 * y1 - x1 * y2
    return A, B, C

def intersection(L1, L2):
    D = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x, y = Dx / D, Dy / D
        return (x, y)
    return None

def det(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    return ax * by + ay * cx + bx * cy - by * cx - cy * ax - ay * bx

def get_orientation(point, segment):
    start, end = segment
    if point == start or point == end:
        return EQUAL

    result = det(start, end, point)

    if fabs(result) < EPS: return EQUAL
    return ABOVE if result > 0 else BELOW

def get_intersection_point(seg1, seg2, orient):
    _, s1_end = seg1
    if get_orientation(s1_end, seg2) != orient: #check if lines intersect
        line1, line2 = seg1.line, seg2.line
        (s1x_min, _), (s1x_max, _) = seg1
        (s2x_min, _), (s2x_max, _) = seg2
        (x, _) = inter = intersection(line1, line2)
        return inter if s1x_min <= x <= s1x_max and s2x_min <= x <= s2x_max else None
    return None

class Key:
    def __init__(self, segment):
        self.segment = segment
        self.op, _ = segment

    def __lt__(self, other):
        orient = get_orientation(self.op, other.segment) if self.op >= other.op else -get_orientation(other.op, self.segment)
        return orient == ABOVE or (orient == EQUAL and get_orientation(self.segment[1], other.segment) == ABOVE) 

    def __eq__(self, other):
        return self.segment == other.segment

    def __hash__(self):
        return hash(self.segment)


class Segment(tuple):
    def __new__(self, a, b):
        return tuple.__new__(Segment, (min(a, b), max(a, b)))

    def __init__(self, a, b):
        self.line = line(a, b)

    def __hash__(self):
        return hash(self.line)