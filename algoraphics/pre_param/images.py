"""
images.py
=========
Generate graphics based on images.

"""

import numpy as np
from PIL import Image

from skimage.color import rgb2lab, deltaE_ciede2000
from skimage.filters import sobel
from skimage.morphology import watershed
from skimage.measure import find_contours, approximate_polygon
from skimage.segmentation import slic, find_boundaries
from skimage.filters import gaussian

from io import BytesIO
from base64 import b64encode

from .main import sample_points_in_shape, centroid, set_style
from .color import average_color


def open_image(path):
    """Load a PIL image from file."""
    image = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
    return image.convert('RGB')  # remove transparency coordinate from PNGs


def encode_image(image, frmt):
    """Encode an image as a data string.

    Used to embed images in SVG.

    Args:
        image (Image): A PIL image.
        frmt (str): Either 'JPEG' or 'PNG'.

    Returns:
        str: The image encoding.

    """
    formats = dict(JPEG='jpg', PNG='png')
    enc = BytesIO()
    image.save(enc, format=frmt)
    data = b64encode(enc.getvalue()).decode('utf-8')
    return 'data:image/' + formats[frmt] + ';base64,' + data


def array_to_image(array, scale=True):
    """Create an image from a 2D or 3D array.

    Args:
        array (numpy.ndarray): A numpy array: 2D for grayscale or 3D for RGB.
        scale (bool): If True, values in 2D array will be scaled so that the highest values are 255 (white).

    Returns:
        Image: A PIL image in RGB mode.

    """
    if scale and len(array.shape) == 2:
        array = 255. * array / np.max(array)
    if len(array.shape) == 2:
        return Image.fromarray(array).convert('RGB')
    else:
        return Image.fromarray(array, mode='RGB')


def resize_image(image, width, height):
    """Downscale an image.

    Scales according to whichever of width or height is not None. Only
    scales down.

    Args:
        image (Image): A PIL image.
        width (int): The new width.  If None, scales according to height.
        height (int): The new height.  If None, scales according to width.

    """
    w, h = image.size
    # if width is not None:
    #     height = int(h * (width / float(w)))
    # elif height is not None:
    #     width = int(w * (height / float(h)))
    # return image.resize((width, height))
    if width is None:
        width = w
    if height is None:
        height = h
    image.thumbnail((width, height))


def sample_colors(image, points):
    """Sample colors from an image.

    Args:
        image (Image): A PIL image.
        points (list|tuple): A list of image coordinates, or a single coordinate.

    Returns:
        list: A list of colors corresponding to `points`, or a single color if input is a single point.

    """
    if type(points) is tuple:
        return sample_colors(image, [points])[0]
    pixels = image.load()
    # Sample from nearest pixel if point is out of range:
    points = [(max(0, p[0]), max(0, p[1])) for p in points]
    points = [(min(p[0], image.size[0] - 1), min(p[1], image.size[1] - 1))
              for p in points]
    return [pixels[p[0], p[1]] for p in points]


def region_color(outline, image, n_points=10):
    """Find representative color for an image region.

    Args:
        outline (shape): A shape corresponding to an image region to sample.
        image (Image): A PIL image.
        n_points (int): Number of points to sample.

    Returns:
        Color: The average color of the sampled image points.

    """
    points = sample_points_in_shape(outline, n_points)
    return average_color(sample_colors(image, points))


def fill_shapes_from_image(shapes, image):
    """Fill shapes according to their corresponding image region.

    Faster than region_color which samples points, but should only be
    used for regular shapes like tiles since it colors according to
    the centroid, which may not be inside the shape if it is
    irregular.

    Args:
        shapes (list): A list of shapes.
        image (Image): A PIL image.

    """
    centroids = [centroid(shape) for shape in shapes]
    colors = sample_colors(image, centroids)
    for i in range(len(shapes)):
        set_style(shapes[i], 'fill', colors[i])


def color_distances(pixels, color):
    """Get color distance from reference color for every pixel.

    Args:
        pixels (numpy.ndarray): A 3D array corresponding to RGB pixels.
        color (rgb): A reference color.

    Returns:
        numpy.ndarray: A 2D array of distances between 0 and 1.

    """
    x = np.zeros_like(pixels)
    x[:, :] = color
    # kL>1 puts less emphasis on lightness
    return deltaE_ciede2000(rgb2lab(pixels), rgb2lab(x), kL=2) / 100.


def segment_image(image, n_segments=100, compactness=10, smoothness=0):
    """Divide image into segments.

    Used by image_regions().

    Args:
        image (Image): A PIL image.
        n_segments (int): Approximate number of desired segments.
        compactness (float): A higher value produces more compact, square-like segments.  Try values along log-scale, e.g. 0.1, 1, 10, 100.
        smoothness (float): The width of gaussian smoothing applied before segmentation.

    Returns:
        numpy.ndarray: A 2D array of integer segment labels.

    """
    return slic(np.array(image), n_segments, compactness,
                sigma=smoothness, min_size_factor=0.1)


def pad_array(pixels, margin=1):
    """Create a new pixel array with added padding.

    Adds additional rows and columns of zeros to four edges of matrix.
    Used to enable finding a contour around a segment at the edge of
    an image and to allow segments to be expanded to overlap each
    other.

    Args:
        pixels (numpy.ndarray): A 2D array of pixels.
        margin (int): The width of padding on each side.

    Returns:
        numpy.ndarray: A 2D array with 2 * `margin` added to both dimensions.

    """
    for i in range(margin):
        pixels = np.insert(pixels, 0, 0, axis=0)
        pixels = np.insert(pixels, 0, 0, axis=1)
        pixels = np.insert(pixels, pixels.shape[0], 0, axis=0)
        pixels = np.insert(pixels, pixels.shape[1], 0, axis=1)
    return pixels


# def segments_to_polygons(seg, simplify=None):
#     """seg is 2d array, simplify is max distance from edge to actual boundary when reducing number of polygon points"""
#     bound = find_boundaries(seg)
#     bound[0, :] = 1
#     bound[-1, :] = 1
#     bound[:, 0] = 1
#     bound[:, -1] = 1
#
#     polygons = find_contours(bound, 0.5)
#     if simplify is not None:
#         polygons = [approximate_polygon(polygon, simplify) for polygon in polygons]
#     polygons = [list(polygon[:, ::-1]) for polygon in polygons]
#     return [[tuple(p) for p in polygon] for polygon in polygons]


def segments_to_shapes(seg, simplify=None, expand=1, curvature=0.2):
    """Convert an array of segment labels to spline shapes.

    Used by image_regions().

    Args:
        seg (numpy.ndarray): A 2D array of segment labels.
        simplify (float): Maximum distance from the edge of a simplified shape to the actual boundary when reducing number of points, or None for no simplification.
        expand (int): Number of pixels to expand each segment in every direction to avoid gaps between adjacent shapes.
        curvature (float): The degree of curvature for the splines.  Usually between zero and one.

    Returns:
        list: A list of spline shapes, generally in order from left to
        right and then bottom to top.

    """
    shapes = []
    for label in np.unique(seg):
        region = seg == label
        region = pad_array(region, expand + 1)
        for i in range(expand):
            region = np.logical_or(region, find_boundaries(region)) * 1
        points = find_contours(region, 0.5)[0]
        points = points - expand - 1  # shift back to original coordinates
        if simplify is not None:
            points = approximate_polygon(points, simplify)
        points = list(points[:, ::-1])
        points = [tuple(p) for p in points]
        shapes.append(dict(type='spline', points=points,
                           curvature=curvature, circular=True))
    return shapes


def image_regions(image, n_segments=100, compactness=10, smoothness=0,
                  simplify=1, expand=2, curvature=0.2):
    """Get spline shapes corresponding to image regions.

    Args:
        image (Image): A PIL image.
        n_segments (int): Approximate number of desired segments.
        compactness (float): A higher value produces more compact, square-like segments.  Try values along log-scale, e.g. 0.1, 1, 10, 100.
        smoothness (float): The width of gaussian smoothing applied before segmentation.
        simplify (float): Maximum distance from the edge of a simplified shape to its actual boundary when reducing the number of points, or None for no simplification.
        expand (int): Number of pixels to expand each segment in every direction to avoid gaps between adjacent shapes.
        curvature (float): The degree of curvature in spline.  Usually between zero and one.

    Returns:
        list: A list of spline shapes, generally in order from left to
        right and then bottom to top.

    """
    seg = segment_image(image, n_segments, compactness, smoothness)
    return segments_to_shapes(seg, simplify, expand, curvature)


def get_color_regions(image, color, smoothness=5, in_param=0.05,
                      out_param=0.3):
    """Get shapes corresponding to image regions matching a color."""
    pixels = np.array(image)
    pixels = color_distances(pixels, color)
    pixels = gaussian(pixels, sigma=smoothness)

    edges = sobel(pixels)

    markers = np.zeros_like(pixels)
    markers[pixels < in_param] = 1
    markers[pixels > out_param] = 2

    segmentation = watershed(edges, markers)

    regions = find_contours(segmentation, 1.5)
    regions = [approximate_polygon(region, smoothness) for region in regions]

    # TODO: sort regions by size
    return [list(region[:, ::-1]) for region in regions]
