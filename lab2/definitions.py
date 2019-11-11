import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
import matplotlib.colors as mcolors
import json as js
from threading import Timer

from random import uniform, choice
from math import sin, cos, pi, inf
from matplotlib.widgets import Button

def setInterval(timer, task):
    isStop = task()
    if not isStop:
        Timer(timer, setInterval, [timer, task]).start()

stop = False
def plot(*args, ax=None):
    ax = ax or plt.axes()
    m, M = 10, -10
    for d in args:
        color = d.get('color') or 'blue'
        points = d['points']
        if len(points) == 0:
            continue
        
        x, y = zip(*np.array(points))
        min_x, max_x = min(x), max(x)
        min_y, max_y = min(y), max(y)
        m, M = min(min_x, min_y, m), max(max_x, max_y, M)
        ax.scatter(x, y, c=color, marker=None)
    ax.autoscale()
    ax.set_aspect('equal')
    m = m * 1.1 - 5
    M = M * 1.1 + 5
    ax.set_xlim(m, M)
    ax.set_ylim(m, M)
    plt.draw()

def generate_dataset(size, fn):
    return [fn() for _ in range(size)]

def line(u, v):
    ux, uy = u
    vx, vy = v
    if (ux == vx): return lambda x: uy
    a = (uy - vy) / (ux - vx) 
    b = vy - a * vx
    return lambda x: a * x + b

def random_point_in_ranges(x_range, y_range):
    return lambda: (uniform(*x_range), uniform(*y_range))

def random_point_on_circle(center, r):
    cx, cy = center
    def generate():
        angle = uniform(0, 2 * pi)
        return (cx + cos(angle) * r, cy + sin(angle) * r)
    return generate

def random_point_on_line(a, b, x_range):
    f = line(a, b)
    min_x, max_x = x_range 
    def generate():
        x = uniform(min_x, max_x)
        y = f(x)
        return (x, y)
    return generate

def random_point_on_segment(a, b):
    ax, ay = a
    bx, by = b

    if ax == bx:
        y_min, y_max = min(ay, by), max(ay, by)
        def generate():
            y = uniform(y_min, y_max)
            return (ax, y)
        return generate
    else:
        f = line(a, b)
        x_min, x_max = min(ax, bx), max(ax, bx)
        def generate():
            x = uniform(x_min, x_max)
            return (x, f(x))
        return generate

def random_point_on_rect(verts):
    a, b, c, d = verts
    lines = [
        random_point_on_segment(a, b),
        random_point_on_segment(b, c),
        random_point_on_segment(c, d),
        random_point_on_segment(d, a)
    ]
    def generate():
        line = choice(lines)
        return line()
    return generate

def det(a, b, c):
    (ax, ay) = a
    (bx, by) = b
    (cx, cy) = c
    return ax * by + ay * cx + bx * cy - by * cx - cy * ax - ay * bx


def det2(a, b, c):
    (ax, ay) = a
    (bx, by) = b
    (cx, cy) = c
    return (ax - cx) * (by - cy) - (ay - cy) * (bx - cx)
class _Button_callback(object):
    def __init__(self, scenes):
        self.i = 0
        self.scenes = scenes
        self.timer = None

    def set_axis(self, ax):
        self.ax = ax

    def next(self, event):
        self.i = (self.i + 1) % len(self.scenes)
        self.draw()

    def prev(self, event):
        self.i = (self.i - 1) % len(self.scenes)
        self.draw()
    
    def play(self, event):
        global stop
        stop = False
        def play():
            global stop
            if stop:
                return True
            if self.i < len(self.scenes):
                self.i += 1
                self.draw()
                return False
            else:
                return True
        setInterval(0.1, play)

    def draw(self):
        self.ax.clear()
        for collection in self.scenes[self.i].points:
            if len(collection.points) > 0:
                self.ax.scatter(*zip(*(np.array(collection.points))), c=collection.color, marker=collection.marker)
        for collection in self.scenes[self.i].lines:
            self.ax.add_collection(collection.get_collection())
        self.ax.autoscale()
        plt.draw()

class Scene:
    def __init__(self, points=[], lines=[]):
        self.points=points
        self.lines=lines

class PointsCollection:
    def __init__(self, points = [], color = None, marker = None):
        self.points = np.array(points)
        self.color = color
        self.marker = marker

class LinesCollection:
    def __init__(self, lines = [], color = None):
        self.color = color
        self.lines = lines
        
    def add(self, line):
        self.lines.append(line)
        
    def get_collection(self):
        if self.color:
            return mcoll.LineCollection(self.lines, colors=mcolors.to_rgba(self.color))
        else:
            return mcoll.LineCollection(self.lines)
            


class Plot:
    def __init__(self, scenes = [], json = None):
        global stop
        stop = True
        if json is None:
            self.scenes = scenes
        else:
            self.scenes = [Scene([PointsCollection(pointsCol) for pointsCol in scene["points"]], 
                                 [LinesCollection(linesCol) for linesCol in scene["lines"]]) 
                           for scene in js.loads(json)]
        
    def __configure_buttons(self, callback):
        plt.subplots_adjust(bottom=0.2)
        axprev = plt.axes([0.6, 0.05, 0.15, 0.075])
        axnext = plt.axes([0.76, 0.05, 0.15, 0.075])
        axplay = plt.axes([0.6 - 0.16, 0.05, 0.15, 0.075])
        bnext = Button(axnext, 'Następny')
        bnext.on_clicked(callback.next)
        bprev = Button(axprev, 'Poprzedni')
        bprev.on_clicked(callback.prev)
        bpplay = Button(axplay, 'Play')
        bpplay.on_clicked(callback.play)
        return [bpplay, bprev, bnext]

    def draw(self):
        plt.close()
        callback = _Button_callback(self.scenes)
        self.widgets = self.__configure_buttons(callback)
        callback.set_axis(plt.axes())
        plt.show()
        callback.draw()
        
    def toJSON(self):
        return js.dumps([{"points": [pointCol.points.tolist() for pointCol in scene.points], 
                          "lines":[linesCol.lines for linesCol in scene.lines]} 
                         for scene in self.scenes])



def flip(x):
    a, b = x
    return b, a

def dist_sq(a, b):
    x1, y1 = a
    x2, y2 = b
    return (x1 - x2) ** 2 + (y1 - y2) ** 2

def genLines(points):
    if (len(points) < 2):
        return []
    lines = []
    size = len(points)
    for i in range(size-1):
        lines.append([points[i], points[(i + 1) % size]])
    return lines

def min_index(xs, key):
    min_val_key, index = key(xs[0]), 0
    for i, val in enumerate(xs):
        val_key = key(val)
        if val_key < min_val_key:
            min_val_key = val_key
            index = i
    return index

INLINE = COLL = 0
LEFT = CCW = 1
RIGHT = CW = -1

def orientation(a, b, c, det=det, eps=10**-12):
    d = det(a, b, c)
    if abs(d) < eps:
        return COLL
    return CCW if d > 0 else CW

def save(result, file):
    with open(file, 'w') as file:
        js.dump(result, file)