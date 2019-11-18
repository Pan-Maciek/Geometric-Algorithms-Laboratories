import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
import matplotlib.colors as mcolors
import json as js
from threading import Timer
from defs import Segment, line

from random import uniform, choice
from math import sin, cos, pi, inf, floor, fabs, hypot
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
# def play(self, event):
#     global stop
#     stop = False
#     def play():
#         global stop
#         if stop:
#             return True
#         if self.i < len(self.scenes):
#             self.i += 1
#             self.draw()
#             return False
#         else:
#             return True
#     setInterval(0.1, play)

class _Button_callback(object):
    def __init__(self, scenes):
        self.i = 0
        self.scenes = scenes
        self.adding_points = False
        self.added_points = []
        self.adding_lines = False
        self.added_lines = []

    def set_axes(self, ax):
        self.ax = ax
        
    def next(self, event):
        self.i = (self.i + 1) % len(self.scenes)
        self.draw(autoscaling = True)

    def prev(self, event):
        self.i = (self.i - 1) % len(self.scenes)
        self.draw(autoscaling = True)
        
    def add_point(self, event):
        self.adding_points = not self.adding_points
        self.new_line_point = None
        if self.adding_points:
            self.adding_lines = False
            self.added_points.append(PointsCollection())
         
    def add_line(self, event):
        self.adding_lines = not self.adding_lines
        self.new_line_point = None
        if self.adding_lines:
            self.adding_points = False
            self.added_lines.append(LinesCollection())

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        new_point = (event.xdata, event.ydata)
        if self.adding_points:
            self.added_points[-1].add_points([new_point])
            self.draw(autoscaling = False)
        elif self.adding_lines:
            if self.new_line_point is not None:
                self.added_lines[-1].add([self.new_line_point, new_point])
                self.new_line_point = None
                self.draw(autoscaling = False)
            else:
                self.new_line_point = new_point
        
    def draw(self, autoscaling = True):
        if not autoscaling:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
        self.ax.clear()
        for collection in (self.scenes[self.i].lines + self.added_lines):
            self.ax.add_collection(collection.get_collection())
        for collection in (self.scenes[self.i].points + self.added_points):
            if len(collection.points) > 0:
                self.ax.scatter(*zip(*(np.array(collection.points))), **collection.kwargs)
        self.ax.autoscale(autoscaling)
        if not autoscaling:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
        plt.draw()

class Scene:
    def __init__(self, points=[], lines=[]):
        self.points=points
        self.lines=lines

class PointsCollection:
    def __init__(self, points = [], **kwargs):
        self.points = points
        self.kwargs = kwargs
    
    def add_points(self, points):
        self.points = self.points + points

class LinesCollection:
    def __init__(self, lines = [], **kwargs):
        self.lines = lines
        self.kwargs = kwargs
        
    def add(self, line):
        self.lines.append(line)
        
    def get_collection(self):
        return mcoll.LineCollection(self.lines, **self.kwargs)
    
class Plot:
    def __init__(self, scenes = [Scene()], json = None):
        if json is None:
            self.scenes = scenes
        else:
            self.scenes = [Scene([PointsCollection(pointsCol) for pointsCol in scene["points"]], 
                                 [LinesCollection(linesCol) for linesCol in scene["lines"]]) 
                           for scene in js.loads(json)]
        
    def __configure_buttons(self, callback):
        plt.subplots_adjust(bottom=0.2)
        ax_prev = plt.axes([0.6, 0.05, 0.15, 0.075])
        ax_next = plt.axes([0.76, 0.05, 0.15, 0.075])
        ax_add_point = plt.axes([0.44, 0.05, 0.15, 0.075])
        ax_add_line = plt.axes([0.28, 0.05, 0.15, 0.075])
        b_next = Button(ax_next, 'Następny')
        b_next.on_clicked(callback.next)
        b_prev = Button(ax_prev, 'Poprzedni')
        b_prev.on_clicked(callback.prev)
        b_add_point = Button(ax_add_point, 'Dodaj punkt')
        b_add_point.on_clicked(callback.add_point)
        b_add_line = Button(ax_add_line, 'Dodaj linię')
        b_add_line.on_clicked(callback.add_line)
        return [b_prev, b_next, b_add_point, b_add_line]
    
    
    def add_scene(self, scene):
        self.scenes.append(scene)
    
    def add_scenes(self, scenes):
        self.scenes = self.scenes + scenes
        
    def toJson(self):
        return js.dumps([{"points": [np.array(pointCol.points).tolist() for pointCol in scene.points], 
                          "lines":[linesCol.lines for linesCol in scene.lines]} 
                         for scene in self.scenes])
    
    def get_added_points(self):
        if self.callback:
            return self.callback.added_points
        else:
            return None
  
    def get_added_lines(self):
        if self.callback:
            return self.callback.added_lines
        else:
            return None
    
    def get_added_elements(self):
        if self.callback:
            return Scene(self.callback.added_points, self.callback.added_lines)
        else:
            return None
    
    def draw(self):
        plt.close()
        fig = plt.figure()
        self.callback = _Button_callback(self.scenes)
        self.widgets = self.__configure_buttons(self.callback)
        ax = plt.axes(autoscale_on = False)
        self.callback.set_axes(ax)
        fig.canvas.mpl_connect('button_press_event', self.callback.on_click)
        plt.show()
        self.callback.draw()
        


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

def get_segments_from_plot(plot):
    return [Segment(u, v) for u, v in plot.get_added_elements().lines[0].lines]
default_lines = [
    Segment((0,0), (10,10)),
    Segment((1,9), (9,1)),
    Segment((3,8), (10,4)),
    Segment((5.6,6), (9,2)),
    Segment((6,3), (11,6)),
    Segment((1.5,9.5), (3.5,1.5))
]

def dist(line, point):
    A, B, C = line
    x, y = point
    return fabs(A * x + B * y + C) / hypot(A, B)

def generate_n_segments(n, min_point, max_point, min_dist=0.1):
    min_x, min_y = min_point
    max_x, max_y = max_point
    
    segments = []
    def gen_point():
        valid = False
        while not valid:
            x = uniform(min_x, max_x)
            y = uniform(min_y, max_y)
            for seg in segments:
                d = dist(seg.line, (x, y))
                if d < min_dist:
                    valid = False
                    break
            else:
                valid = True
        return x, y
    
    for _ in range(n):
        start, end = gen_point(), gen_point()
        while start[0] == end[0]:
            start, end = gen_point(), gen_point()
        segments.append(Segment(start, end))
    return segments

def save_to(segments, file='data1.json'):
    with open(file, 'w') as file:
        js.dump(segments, file)

def load(file='data1.json'):
    with open(file, 'r') as file:
        return [Segment((x1, y1), (x2, y2)) for ((x1, y1), (x2, y2)) in js.load(file)]
        