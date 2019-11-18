from sortedcontainers.sortedset import SortedSet
from defs import *
from queue import PriorityQueue
from definitions import *


def algo_visual(data_set):
    events = prepare_events(data_set)
    state = SortedSet() # (point, event, [skey])
    intersections = []
    points = []
    all_lines = LinesCollection(data_set, color='gray')
    yield Scene([ ],[ all_lines ])

    def get_neighbours(segment):
        index = state.index(segment)
        return (state[index - 1].segment if index > 0 else None, #above
            state[index + 1].segment if index < len(state) - 1 else None) #bellow


    def swap_on(point, segments):
        above, below = segments
        state.remove(above)
        state.remove(below)

        above.op = below.op = point

        state.add(above)
        state.add(below)

    def add_intersection_if_exists(segment, neighbour, orientation):
        if neighbour and segment:
            point = get_intersection_point(segment, neighbour, orientation)
            if point:
                inter = tuple(sorted([segment, neighbour]))
                if inter not in intersections:
                    intersections.append(inter)
                    points.append(point)
                    events.put((point, INTERSECT, [Key(segment), Key(neighbour)]))


    def add_intersections(state, skey):
        above, below = get_neighbours(skey)
        add_intersection_if_exists(skey.segment, above, BELOW)
        add_intersection_if_exists(skey.segment, below, ABOVE)

    for point, event, segments in iter_events(events):
        if event == START:
            [skey] = segments
            state.add(skey)
            add_intersections(state, skey)
            above, below = get_neighbours(skey)
            yield Scene([ 
                PointsCollection(points[:], color='green'),
                PointsCollection([point], color='red'),
            ],[ 
                all_lines,
                LinesCollection([x.segment for x in state], color='blue'),
                *([LinesCollection([above], color='red')] if above else []),
                *([LinesCollection([below], color='green')] if below else [])
            ])
        elif event == END:
            [skey] = segments
            above, below = get_neighbours(skey)
            state.remove(skey)
            add_intersection_if_exists(above, below, ABOVE)
            yield Scene([ 
                PointsCollection(points[:], color='green'),
                PointsCollection([point], color='red'),
            ],[ 
                all_lines,
                LinesCollection([x.segment for x in state], color='blue'),
                *([LinesCollection([above], color='red')] if above else []),
                *([LinesCollection([below], color='green')] if below else []),
            ])
        else:
            above, below = segments
            swap_on(point, segments)

            add_intersections(state, above)
            add_intersections(state, below)
            yield Scene([ 
                PointsCollection(points[:], color='green'),
                PointsCollection([point], color='red'),
            ],[ 
                all_lines,
                LinesCollection([x.segment for x in state], color='blue'),
                LinesCollection([below.segment], color='red'),
                LinesCollection([above.segment], color='green')
            ])
    yield Scene([ 
        PointsCollection(points[:], color='green')
    ],[ all_lines ])

def simple_visual(data_set):
    events = prepare_events(data_set)
    state = SortedSet() # (point, event, [skey])

    all_lines = LinesCollection(data_set, color='gray')
    yield Scene([ ],[ all_lines ])

    def get_neighbours(segment):
        index = state.index(segment)
        return (state[index - 1].segment if index > 0 else None, #above
            state[index + 1].segment if index < len(state) - 1 else None) #bellow


    def check_if_intersection_exists(segment, neighbour, orientation):
        if neighbour and segment:
            point = get_intersection_point(segment, neighbour, orientation)
            return point

    def check_intersections(state, skey):
        above, below = get_neighbours(skey)
        return check_if_intersection_exists(skey.segment, above, BELOW) or \
               check_if_intersection_exists(skey.segment, below, ABOVE)

    for point, event, [skey] in iter_events(events):
        if event == START:
            state.add(skey)
            ipoint = check_intersections(state, skey)
        elif event == END:
            above, below = get_neighbours(skey)
            state.remove(skey)
            ipoint = check_if_intersection_exists(above, below, ABOVE)
        yield Scene([ 
            PointsCollection([point], color='red'),
        ],[ 
            all_lines,
            LinesCollection([x.segment for x in state], color='blue')
        ])
        if ipoint:
            break
    yield Scene([ 
        PointsCollection([ipoint], color='green'),
    ],[ 
        all_lines
    ])