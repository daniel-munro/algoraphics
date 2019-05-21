"""
images.py
=========
Generate graphics based on images.

"""

import numpy as np
from PIL import Image
from skimage.measure import find_contours, approximate_polygon
from skimage.segmentation import slic, find_boundaries
from typing import Union, Tuple, Sequence

from .shapes import sample_points_in_shape, centroid, spline, set_style
from .color import Color, average_color

Number = Union[int, float]
Point = Tuple[Number, Number]


def open_image(path: str) -> "Image":
    """Load a PIL image from file.

    Args:
        path: Path to the image file.

    Returns:
        A PIL Image.

    """
    image = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
    return image.convert("RGB")  # Remove transparency coordinate from PNGs.


def resize_image(image: "Image", width: int, height: int):
    """Downscale an image.

    Scales according to whichever of width or height is not None. Only
    scales down.

    Args:
        image: A PIL image.
        width: The new width.  If None, scales according to height.
        height: The new height.  If None, scales according to width.

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


def sample_colors(
    image: "Image", points: Union[Point, Sequence[Point]]
) -> Union[Color, Sequence[Color]]:
    """Sample colors from an image.

    Args:
        image: A PIL image.
        points: A list of image coordinates, or a single coordinate.

    Returns:
        A list of colors corresponding to ``points``, or a single
        color if input is a single point.

    """
    if type(points) is tuple:
        return sample_colors(image, [points])[0]
    pixels = image.load()
    # Sample from nearest pixel if point is out of range:
    points = [(max(0, p[0]), max(0, p[1])) for p in points]
    points = [
        (min(p[0], image.size[0] - 1), min(p[1], image.size[1] - 1)) for p in points
    ]
    return [Color(RGB=pixels[int(p[0]), int(p[1])]) for p in points]


def region_color(outline: dict, image: "Image", n_points: int = 10) -> Color:
    """Find representative color for an image region.

    Args:
        outline: A shape corresponding to an image region to sample.
        image: A PIL image.
        n_points: Number of points to sample.

    Returns:
        The average color of the sampled image points.

    """
    points = sample_points_in_shape(outline, n_points)
    return average_color(sample_colors(image, points))


def fill_shapes_from_image(shapes: Sequence[dict], image: "Image"):
    """Fill shapes according to their corresponding image region.

    Faster than region_color which samples points, but should only be
    used for regular shapes like tiles since it colors according to
    the centroid, which may not be inside the shape if it is
    irregular.

    Args:
        shapes: A list of shapes.
        image: A PIL image.

    """
    centroids = [centroid(shape) for shape in shapes]
    colors = sample_colors(image, centroids)
    for i in range(len(shapes)):
        set_style(shapes[i], "fill", colors[i])


def _segment_image(
    image: "Image",
    n_segments: int = 100,
    compactness: Number = 10,
    smoothness: Number = 0,
) -> np.ndarray:
    """Divide image into segments.

    Used by image_regions().

    Args:
        image: A PIL image.
        n_segments: Approximate number of desired segments.
        compactness: A higher value produces more compact, square-like
          segments.  Try values along log-scale, e.g. 0.1, 1, 10, 100.
        smoothness: The width of gaussian smoothing applied before
          segmentation.

    Returns:
        A 2D array of integer segment labels.

    """
    return slic(
        np.array(image), n_segments, compactness, sigma=smoothness, min_size_factor=0.1
    )


def pad_array(pixels: np.ndarray, margin: int = 1) -> np.ndarray:
    """Create a new pixel array with added padding.

    Adds additional rows and columns of zeros to four edges of matrix.
    Used to enable finding a contour around a segment at the edge of
    an image and to allow segments to be expanded to overlap each
    other.

    Args:
        pixels: A 2D array of pixels.
        margin: The width of padding on each side.

    Returns:
        A 2D array with 2 * ``margin`` added to both dimensions.

    """
    for i in range(margin):
        pixels = np.insert(pixels, 0, 0, axis=0)
        pixels = np.insert(pixels, 0, 0, axis=1)
        pixels = np.insert(pixels, pixels.shape[0], 0, axis=0)
        pixels = np.insert(pixels, pixels.shape[1], 0, axis=1)
    return pixels


def _segments_to_shapes(
    seg: np.ndarray, simplify: Number = None, expand: int = 1, smoothing: float = 0.2
) -> Sequence[dict]:
    """Convert an array of segment labels to spline shapes.

    Used by ``image_regions()``.

    Args:
        seg: A 2D array of segment labels.
        simplify: Maximum distance from the edge of a simplified shape
          to the actual boundary when reducing number of points, or
          None for no simplification.
        expand: Number of pixels to expand each segment in every
          direction to avoid gaps between adjacent shapes.
        smoothing: The degree of curvature for the splines.  Usually
          between zero and one.

    Returns:
        A list of spline shapes, generally in order from left to right
        and then bottom to top.

    """
    shapes = []
    for label in np.unique(seg):
        region = seg == label
        region = pad_array(region, expand + 1)
        for i in range(expand):
            region = np.logical_or(region, find_boundaries(region)) * 1
        points = find_contours(region, 0.5)[0]
        points = points - expand - 1  # Shift back to original coordinates.
        if simplify is not None:
            points = approximate_polygon(points, simplify)
        points = list(points[:, ::-1])
        points = [tuple(p) for p in points]
        shapes.append(spline(points=points, smoothing=smoothing, circular=True))
    return shapes


def image_regions(
    image: "Image",
    n_segments: int = 100,
    compactness: Number = 10,
    smoothness: Number = 0,
    simplify: Number = 1,
    expand: int = 2,
    smoothing: float = 0.2,
) -> Sequence[dict]:
    """Get spline shapes corresponding to image regions.

    Args:
        image: A PIL image.
        n_segments: Approximate number of desired segments.
        compactness: A higher value produces more compact, square-like
          segments.  Try values along log-scale, e.g. 0.1, 1, 10, 100.
        smoothness: The width of gaussian smoothing applied before
          segmentation.
        simplify: Maximum distance from the edge of a simplified shape
          to its actual boundary when reducing the number of points,
          or None for no simplification.
        expand: Number of pixels to expand each segment in every
          direction to avoid gaps between adjacent shapes.
        smoothing: The degree of curvature in spline.  Usually between
          zero and one.

    Returns:
        A list of spline shapes, generally in order from left to right
        and then bottom to top.

    """
    seg = _segment_image(image, n_segments, compactness, smoothness)
    return _segments_to_shapes(seg, simplify, expand, smoothing)
