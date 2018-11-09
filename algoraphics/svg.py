"""
svg.py
======
write SVG files.

"""

import random
import string
import subprocess

from .main import flatten, scale_shapes, translate_shapes
from .paths import _write_path, _spline_path
from .images import encode_image
from .color import Color


def _match_dict(dicts, d):
    """Return index of dictionary in `dicts` matching `d`, or None if no match."""
    for i in range(len(dicts)):
        if dicts[i] == d:
            return i
    return None


def write_object(obj, defs, filters):
    """Generate SVG representation of object.

    Args:
        obj (dict): A shape, group, text, or image dictionary.
        defs (list): A list of strings used to collect SVG representations of all clip paths, filters, etc.
        filters (list): A collection of filter dictionaries used thus far so that duplicate filters can reference the same definition.

    Returns:
        str: An SVG encoding.

    """
    if obj['type'] == 'polygon':
        points = ' '.join([str(x[0]) + ',' + str(x[1]) for x in obj['points']])
        output = '<polygon points="' + points + '" '

    elif obj['type'] == 'path':
        output = '<path d="' + _write_path(obj['d']) + '" '
        # if 'transform' in obj:
        #     output += 'transform="' + obj['transform'] + '" '
        if 'style' in obj and 'fill' not in obj['style']:
            obj['style']['fill'] = 'none'

    elif obj['type'] == 'spline':
        if 'curvature' not in obj:
            obj['curvature'] = 0.3
        if 'circular' not in obj:
            obj['circular'] = False
        d = _spline_path(obj['points'], obj['curvature'], obj['circular'])
        output = '<path d="' + d + '" '
        if 'style' in obj and 'fill' not in obj['style']:
            obj['style']['fill'] = 'none'

    elif obj['type'] == 'circle':
        output = ('<circle cx="' + str(obj['c'][0]) + '" cy="'
                  + str(obj['c'][1]) + '" r="' + str(obj['r']) + '" ')

    elif obj['type'] == 'line':
        output = ('<line x1="' + str(obj['p1'][0]) + '" y1="'
                  + str(obj['p1'][1]) + '" x2="' + str(obj['p2'][0])
                  + '" y2="' + str(obj['p2'][1]) + '" ')

    elif obj['type'] == 'polyline':
        points = ' '.join([str(x[0]) + ',' + str(x[1]) for x in obj['points']])
        output = '<polyline points="' + points + '" fill="none" '

    elif obj['type'] == 'text':
        align = obj['align']
        if align == 'left':
            text_anchor = 'start'
        elif align == 'center':
            text_anchor = 'middle'
        elif align == 'right':
            text_anchor = 'end'
        output = '<text x="' + str(obj['x']) + '" y="' + str(obj['y']) + '" '
        output += 'text-anchor="' + text_anchor + '" '
        output += 'font-size="' + str(obj['font_size']) + '" '
        # output += 'transform="translate(0, ' + str(2 * obj['y']) + ') scale(1, -1)" '

    elif obj['type'] == 'image':
        # output = '<image x="' + str(obj['x']) + '" y="' + str(obj['y']) + '" width="' + str(obj['width']) + '" height="' + str(obj['height']) + '" xlink:href="' + obj['ref'] + '"'
        output = '<image '
        if 'w' not in obj:
            obj['w'] = obj['image'].width
        if 'h' not in obj:
            obj['h'] = obj['image'].height
        if 'x' in obj:
            output += 'x="' + str(obj['x']) + '" '
        if 'y' in obj:
            output += 'y="' + str(obj['y']) + '" '
        output += ('width="' + str(obj['w']) + '" height="' + str(obj['h'])
                   + '" xlink:href="' +
                   encode_image(obj['image'], obj['format']) + '"')

    elif obj['type'] == 'group':
        output = '<g '

        if 'clip' in obj:
            clip_id = ''.join([random.choice(string.ascii_letters) for
                               i in range(8)])
            # if not isinstance(obj['clip'], list):
            #     obj['clip'] = [obj['clip']]
            clip = '<clipPath id="' + clip_id + '">\n'
            clip += ''.join([write_object(o, defs, filters) for o in
                             flatten(obj['clip'])])
            clip += '</clipPath>\n'
            defs.append(clip)
            output += 'clip-path="url(#' + clip_id + ')" '

    if 'style' in obj:
        output += 'style="' + write_style(obj['style']) + '" '

    if 'filter' in obj:
        match = _match_dict(filters, obj['filter'])
        if match is None:
            filters.append(obj['filter'])
            match = len(filters) - 1
        filter_id = 'filter' + str(match)
        output += 'filter="url(#' + filter_id + ')" '

    if obj['type'] == 'group':
        output += '>\n'
        # if not isinstance(obj['members'], list):
        #     obj['members'] = [obj['members']]
        output += ''.join([write_object(o, defs, filters) for o in
                           flatten(obj['members'])])
        output += '</g>\n'
    elif obj['type'] == 'text':
        output += '>' + obj['text'] + '</text>\n'
    else:
        output += ' />\n'

    return output


def write_style(style):
    """Generate an SVG representation of an object's style.

    Args:
        style (dict): A dictionary with attributes as keys. Underscores will be replaced with hyphens, which are not allowed in keys.

    Returns:
        str: An SVG encoding which should be inserted between the
        quotes of style="...".

    """
    style = style.copy()  # keep objects intact for reuse.
    if 'fill' in style and type(style['fill']) is tuple:
        RGB = Color(hsl=style['fill']).RGB()
        style['fill'] = ('rgb('
                         + ', '.join([str(x) for x in RGB])
                         + ')')
    if 'stroke' in style and type(style['stroke']) is tuple:
        RGB = Color(hsl=style['stroke']).RGB()
        style['stroke'] = ('rgb('
                           + ', '.join([str(x) for x in RGB])
                           + ')')

    if 'stroke' in style and style['stroke'] == 'match':
        if 'fill' in style:
            style['stroke'] = style['fill']
        else:
            del style['stroke']

    style = [(prop.replace("_", "-"), value) for prop, value in style.items()]

    return ';'.join([prop + ':' + str(value) for prop, value in style])


def write_filters(filters):
    """Generate an SVG representation of all filters used in graphic.

    Args:
        filters (list): A list of filters.

    Returns:
        str: An SVG encoding.

    """
    fltrs = []
    for i, fltr in enumerate(filters):

        if fltr['type'] == 'shadow':
            f = '<filter id="filter' + str(i) + '" '
            f += 'x="-50%" y="-50%" width="200%" height="200%">\n'
            # f += 'x="-' + str(3 * fltr['stdev']) + '" '
            # f += 'y="-' + str(3 * fltr['stdev']) + '" '
            # f += 'width="' + str(6 * fltr['stdev']) + '" '
            # f += 'height="' + str(6 * fltr['stdev']) + '">\n'
            f += '<feGaussianBlur in="SourceAlpha" '
            f += 'stdDeviation="' + str(fltr['stdev']) + '" result="blur" />\n'
            # f += '<feComponentTransfer><feFuncA type="linear" '
            # f += 'slope="' + str(fltr['darkness']) + '" />'
            # f += '</feComponentTransfer>\n'

            # alt to feComponentTransfer:
            f += ('<feFlood flood-color="black" flood-opacity="'
                  + str(fltr['darkness']) + '" />\n')
            f += '<feComposite in2="blur" operator="in" />\n'
            
            f += ('<feMerge>'
                  + '<feMergeNode /><feMergeNode in="SourceGraphic" />'
                  + '</feMerge>\n')
            f += '</filter>\n'

        # if fltr['type'] == 'shadow':
        #     f = '<filter id="filter' + str(i) + '">\n'
        #     f += '<feDropShadow stdDeviation="' + str(fltr['stdev'])
        #     f += '" dx="0" dy="0" />\n'
        #     f += '</filter>\n'

        elif fltr['type'] == 'roughness':
            # # f += '<feColorMatrix in="diffLight" type="luminanceToAlpha" result="diffLight2" />\n'
            # f += '<feColorMatrix in="diffLight" type="matrix" values="0.3 0 0 0 0  0 0.3 0 0 0  0 0 0.3 0 0  1 0 0 0 0" result="diffLight2" />\n'
            # f += '<feComponentTransfer in="diffLight2" result="diffLight3"><feFuncA type="table" tableValues="0.7 0.4 0 0.2 0.4" /></feComponentTransfer>\n'
            # f += '<feComposite in2="SourceGraphic" in="diffLight3" operator="atop" />\n'

            f = '<filter id="filter' + str(i) + '">\n'
            f += ('<feTurbulence type="fractalNoise" baseFrequency="0.02" '
                  + 'numOctaves="5" result="noise" />\n')
            f += ('<feDiffuseLighting in="noise" lighting-color="white" '
                  + 'surfaceScale="0.5" result="diffLight">\n')
            f += '<feDistantLight azimuth="45" elevation="35" />\n'
            f += '</feDiffuseLighting>\n'

            f += ('<feColorMatrix in="diffLight" type="matrix" '
                  + 'values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  1 0 0 0 0" '
                  + 'result="diffLightLight" />\n')
            f += ('<feColorMatrix in="diffLight" type="matrix" '
                  + 'values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1 0 0 0 1" '
                  + 'result="diffLightShadow" />\n')

            f += ('<feComponentTransfer in="diffLightLight" '
                  + 'result="diffLightLight2">\n')
            f += '<feFuncA type="table" tableValues="0 0 0.8" />\n'
            f += '</feComponentTransfer>\n'

            f += ('<feComponentTransfer in="diffLightShadow" '
                  + 'result="diffLightShadow2">\n')
            f += '<feFuncA type="table" tableValues="0 0 0.5 0.5" />\n'
            f += '</feComponentTransfer>\n'

            f += ('<feComposite in2="SourceGraphic" in="diffLightShadow2" '
                  + 'operator="atop" result="sourceWithShadow" />\n')
            f += ('<feComposite in2="sourceWithShadow" in="diffLightLight2" '
                  + 'operator="atop" />\n')
            f += '</filter>\n'

        fltrs.append(f)
    return fltrs


def write_SVG(objects, w, h, file_name, optimize=True):
    """Write an SVG file for a collection of objects.

    Args:
        objects (dict|list): A (nested) collection of objects.  Placed onto the canvas in order after flattening.
        w (int): Width of canvas.
        h (int): Height of canvas.
        file_name (str): The file name to write to.
        optimize (bool): Whether to optimize the SVG file using svgo.

        """
    defs = []
    filters = []
    out = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
    out += 'xmlns:xlink="http://www.w3.org/1999/xlink" '
    out += 'width="' + str(w) + '" height="' + str(h) + '">\n'

    # flip y-axis so zero is at the bottom:
    scale_shapes(objects, 1, -1)
    translate_shapes(objects, 0, h)

    objects = ''.join([write_object(obj, defs, filters) for obj in
                       flatten(objects)])

    defs.extend(write_filters(filters))
    out += '<defs>\n' + ''.join(defs) + '</defs>\n'

    # flip y-axis so zero is at the bottom:
    # out += '<g transform="translate(0, ' + str(h) + ') scale(1, -1)">\n'
    # out += objects
    # out += '</g>\n</svg>\n'
    out += objects + '</svg>\n'

    open(file_name, 'w').write(out)
    if optimize:
        # TODO: change to subprocess.run().
        # os.system('svgo --quiet --precision=2 '
        #           + '--config=/home/dan/coding/graphics/algoraphics/scripts/'
        #           + 'svgo_config.txt -i ' + file_name)
        subprocess.run([
            'svgo', '--quiet', '--precision=2',
            # '--config=/home/dan/coding/graphics/algoraphics/scripts/svgo_config.txt',
            # '--disable=collapseGroups',
            '--input=' + file_name
        ])


def write_frames(fun, n, w, h, file_name):
    """Write multiple frames of randomized objects.

    Frames can then be combined into an animated GIF.

    Args:
        fun (function): A function called with no arguments that returns an SVG object collection.
        n (int): Number of frames to generate.
        w (int): Width of the canvas.
        h (int): Height of the canvas.
        file_name (str): A file name (without extension) to write to.  File names will be [file_name]_0.svg, etc.

    """
    for i in range(n):
        write_SVG(fun(), w, h, file_name + "_" + str(i) + ".svg")


# def round_values(obj, digits=0):
#     """rounds all values in nested structure"""
#
#     def round_value(value, digits=0):
#         if digits == 0:
#             return int(round(value))
#         else:
#             return round(value, digits)
#
#     def process_item(obj, i):
#         if isinstance(obj[i], (list, dict)):
#             round_values(obj[i], digits)
#         elif isinstance(obj[i], float):
#             obj[i] = round_value(obj[i], digits)
#
#     if isinstance(obj, list):
#         for i in range(len(obj)):
#             process_item(obj, i)
#     else:
#         for field in obj:
#             process_item(obj, field)
