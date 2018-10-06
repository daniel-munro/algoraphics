import numpy as np
from .tiling import *
from .color import *
from .textures import *
from .filaments import *
from .paint import *


def get_color(color):
    if callable(color):
        return color()
    elif type(color) is str:
        return hex_to_rgb(color)
    else:
        return color


def map_frame_tear(objects, width, height):
    margin = 15
    # insert white bg within frame to prevent shadowing objects if
    # empty space present:
    objects.insert(0, background('white', width, height))
    x = [background('white', width, height, margin=2)]
    x.append(tear_paper_rect(objects, (margin, width - margin,
                                       margin, height - margin)))
    return x


# 0D

def map_spot(coords, color):
    color = get_color(color)
    x = dict(type='circle', c=coords[0], r=np.random.uniform(4, 9))
    set_style(x, 'fill', color)
    return x


def map_scribble_dot(coords, color, width=1.5, wildness=20):
    color = get_color(color)
    pts = coords * 20
    jitter_points(pts, wildness / 2, 'gaussian')
    x = dict(type='spline', points=pts)
    set_style(x, 'stroke', color)
    set_style(x, 'stroke_width', width)
    return x


def map_chad(coords, color):
    color = get_color(color)
    x = dict(type='circle', c=coords[0], r=10)
    set_style(x, 'fill', color)
    add_paper_texture(x)
    return with_shadow(x, stdev=2, darkness=0.5)


def map_paint_splat(coords, color, size=10):
    color = get_color(color)
    width = max(3, size / 8.)
    x = blow_paint_spot(coords[0], length=size, width=width)
    set_style(x, 'fill', color)
    return x


# 1D

def map_line(coords, color, width=1):
    color = get_color(color)
    x = dict(type='polyline', points=coords)
    set_style(x, 'stroke', color)
    set_style(x, 'stroke_width', width)
    return x


def map_squiggle(coords, color, width=1.5, density=0.7, wildness=20):
    color = get_color(color)
    interpolate(coords, 1 / density)
    jitter_points(coords, wildness, 'gaussian')
    x = dict(type='spline', points=coords)
    set_style(x, 'stroke', color)
    set_style(x, 'stroke_width', width)
    return x


def map_spot_path(coords, color1, color2, width=20):
    color1 = rgb_to_hsl(get_color(color1))
    color2 = rgb_to_hsl(get_color(color2))
    col_fun = lambda: hsl_to_rgb(color_mixture(color1, color2,
                                               np.random.random(), mode='hsl'))
    interpolate(coords, 80 / width)
    pts = [p for p in coords]
    for i in range(1, len(coords) - 1):
        # jitter sideways only for continuity
        ang = angle_between(coords[i - 1], coords[i], coords[i + 1]) / 2
        p = rotated_point(coords[i - 1], coords[i], ang)
        dev = np.random.randn() * (width / 3)
        pts[i] = move_toward(coords[i], p, dev)
    radii = np.random.permutation(geom_seq(9, 2, len(pts)))
    x = [dict(type='circle', c=pts[i], r=radii[i]) for i in range(len(pts))]
    set_style(x, 'fill', col_fun)
    np.random.shuffle(x)
    return x


def map_curvy_dashed_line(coords, color='black', width=5, curviness=0.8):
    color = get_color(color)
    interpolate(coords, 300 - curviness * 290)
    jitter_points(coords, 20, 'uniform')
    x = dict(type='spline', points=coords)
    set_style(x, 'stroke', color)
    set_style(x, 'stroke_dasharray', '20, 5')
    set_style(x, 'stroke_width', width)
    return x


def map_circuit_trace(coords, color='white'):
    color = get_color(color)
    # shorten ends so that 'intersections' don't actually connect:
    coords[0] = move_toward(coords[0], coords[1], 10)
    coords[-1] = move_toward(coords[-1], coords[-2], 10)
    x = [dict(type='polyline', points=coords)]
    set_style(x, 'stroke', color)
    nodes = [dict(type='circle', c=p, r=3) for p in [coords[0], coords[-1]]]
    set_style(nodes, 'stroke', color)
    set_style(nodes, 'fill', 'black')
    x.extend(nodes)
    return x


def map_paper_strips(coords, color, max_length=200):
    interpolate(coords, max_length)
    strips = []
    dev = lambda: np.random.uniform(20, 50)
    for i in range(len(coords) - 1):
        p1 = rotated_point(coords[i + 1], coords[i], rad(180 - dev()))
        p1 = move_toward(coords[i], p1, 20)
        p2 = rotated_point(coords[i + 1], coords[i], rad(180 + dev()))
        p2 = move_toward(coords[i], p2, 20)
        p3 = rotated_point(coords[i], coords[i + 1], rad(180 - dev()))
        p3 = move_toward(coords[i + 1], p3, 20)
        p4 = rotated_point(coords[i], coords[i + 1], rad(180 + dev()))
        p4 = move_toward(coords[i + 1], p4, 20)
        strips.append(map_paper([p1, p2, p3, p4], color))
    np.random.shuffle(strips)
    return strips


def map_blow_paint_line(coords, color, size=20, spacing=20):
    color = get_color(color)
    width = min(8, size / 8.)
    lw = max(8, size / 2.5)
    x = blow_paint_line(coords, line_width=lw, spacing=spacing, length=size,
                        len_dev=0.33, width=width)
    set_style(x, 'fill', color)
    return x


# 2D

def map_solid(coords, color):
    color = get_color(color)
    x = dict(type='polygon', points=coords)
    set_style(x, 'fill', color)
    set_style(x, 'stroke', 'none')
    return x


def map_scribble(coords, color, width=1.5, density=0.7):
    color = get_color(color)
    # sqrt b/c bigger = more line per pt, so n_pts should be prop. to area
    n_pts = max(5, int(density * 1.5 * math.sqrt(polygon_area(coords))))
    outline = dict(type='polygon', points=coords)
    pts = sample_points_in_shape(outline, n_pts)
    x = dict(type='spline', points=pts)
    set_style(x, 'stroke', color)
    set_style(x, 'stroke_width', width)
    return x


def map_tri_tiles(coords, color, tile_size=300):
    color = get_color(color)
    outline = dict(type='polygon', points=coords)
    x = tile_region(outline, delaunay_regions, tile_size, regularity=3)
    if not callable(color):
        # using default lambda var to evaluate now
       color = lambda c=color: rand_col_nearby(c, 0, 0, 0.1)
    set_style(x['members'], 'fill', color)
    return x


def map_spot_fill(coords, color1, color2):
    color1 = rgb_to_hsl(get_color(color1))
    color2 = rgb_to_hsl(get_color(color2))
    col_fun = lambda: hsl_to_rgb(color_mixture(color1, color2,
                                               np.random.random(), mode='hsl'))
    outline = dict(type='polygon', points=coords)
    x = fill_ishihara_spots(outline, r_min=2, r_max=9)
    set_style(x, 'fill', col_fun)
    return x


def map_marbled(coords, color, contrast=0.3, scale=100):
    color = get_color(color)
    color_dark = color_mixture(color, (0, 0, 0), contrast)
    color_light = color_mixture(color, (255, 255, 255), contrast)
    x = dict(type='polygon', points=coords)
    return billow_region(x, [color, color_dark, color, color_light], scale)


def map_shrubs(coords):
    boundary = dict(type='polygon', points=coords)
    bounds = bounding_box(boundary)
    area = (bounds[1] - bounds[0]) * (bounds[3] - bounds[2])
    # n_shrubs = int(area // 400 + 1)
    # lower density for very large areas:
    n_shrubs = int(area ** 0.75 / 100 + 2)
    locs = mitchell_points(n_shrubs, 5, bounds)
    keep_points_inside(locs, boundary)
    x = []
    for i, loc in enumerate(locs):
        color = rand_col_nearby((0, 150, 0), 0.1, 0.2, 0.1)
        leaves = [tapered_filament(start = loc,
                                   direction = j * 360 / 9,
                                   width = 8,
                                   l_min = 4,
                                   l_max = 9,
                                   segments = 3,
                                   l_max_step = 3) for j in range(9)]
        set_style(leaves, 'fill', color)
        x.append(leaves)
    return x


def map_x(coords, color='red', thickness=8):
    color = get_color(color)
    loc = polygon_centroid(coords)
    width = 40
    x = [dict(type='line',
     	      p1=(loc[0] - width / 2, loc[1] - width / 2),
              p2=(loc[0] + width / 2, loc[1] + width / 2)),
         dict(type='line',
              p1=(loc[0] - width / 2, loc[1] + width / 2),
              p2=(loc[0] + width / 2, loc[1] - width / 2))]
    set_style(x, 'stroke', color)
    set_style(x, 'stroke_width', thickness)
    return x


def map_circuit_component(coords, color='#181818'):
    color = get_color(color)
    x = [dict(type='polygon', points=coords)]
    set_style(x[0], 'fill', color)
    l = math.sqrt(polygon_area(coords)) / 10
    for i in range(len(coords)):
        locs = points_on_line(coords[i], coords[(i + 1) % len(coords)], 6)[1:-1]
        starts = [move_toward(p, rotated_point(coords[i], p, math.pi/2), l / 2) for p in locs]
        ends = [move_toward(p, rotated_point(coords[i], p, -math.pi/2), l / 2) for p in locs]
        wires = [dict(type='line', p1=starts[i], p2=ends[i]) for i in range(len(locs))]
        set_style(wires, 'stroke', '#ccc')
        set_style(wires, 'stroke_width', 2)
        x.extend(wires)
    return x


def map_paper(coords, color):
    color = get_color(color)
    x = dict(type='polygon', points=coords)
    set_style(x, 'fill', color)
    add_paper_texture(x)
    return with_shadow(x, stdev=2, darkness=0.5)


def map_blow_paint_area(coords, color, size=15, spacing=10):
    color = get_color(color)
    width = max(3, size / 8.)
    x = blow_paint_area(coords, spacing=spacing, length=size,
                        len_dev=0.33, width=width)
    set_style(x, 'fill', color)
    return x


map_fun_names = [map_spot, map_scribble_dot, map_chad,
                 map_paint_splat, map_line, map_squiggle,
                 map_spot_path, map_curvy_dashed_line,
                 map_circuit_trace, map_paper_strips,
                 map_blow_paint_line, map_solid, map_scribble,
                 map_tri_tiles, map_spot_fill, map_marbled,
                 map_shrubs, map_x, map_circuit_component, map_paper,
                 map_blow_paint_area]
map_funs = {}
for fun in map_fun_names:
    params = fun.__code__.co_varnames[:fun.__code__.co_argcount]
    map_funs[fun.__name__] = dict(fun=fun, params=params)
