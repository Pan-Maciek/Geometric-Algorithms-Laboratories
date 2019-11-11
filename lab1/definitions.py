import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
import matplotlib.colors as mcolors
import json as js

from random import uniform
from math import sin, cos, pi

def plot(*args):
    ax = plt.axes()
    m, M = -10, 10
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
    m *= 1.1
    M *= 1.1
    ax.set_xlim(m, M)
    ax.set_ylim(m, M)
    plt.draw()

def generate_dataset(size, fn):
    return [fn() for _ in range(size)]

def random_point_in_rect(r):
    return lambda: (uniform(-r, r), uniform(-r, r))

def random_point_on_circle(r):
    def generate():
        angle = uniform(0, 2 * pi)
        return (cos(angle) * r, sin(angle) * r)
    return generate

def line(u, v):
    ux, uy = u
    vx, vy = v
    a = (uy - vy) / (ux - vx) 
    b = vy - a * vx
    return lambda x: a * x + b

def random_point_on_line(a, b, x_range):
    f = line(a, b)
    min_x, max_x = x_range 
    def generate():
        x = uniform(min_x, max_x)
        y = f(x)
        return (x, y)
    return generate

