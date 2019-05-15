Glossary
========

.. glossary::

   bounds
       A tuple giving the minimum x, minimum y, maximum x, and maximum
       y coordinate of a :term:`shape`, :term:`collection`, or general
       rectangular space.

   collection
       A shape or a list containing :term:`shapes<shape>`, which can
       be nested in lists.

   doodle
       An abstraction of a small drawing.  It can vary each time it is
       drawn.  A fill function can draw it in different orientations
       and locations to fill a :term:`region`.

   image
       A PIL Image object specifying a grid of pixels.  These are
       usually used as templates, but can also be drawn using a
       ``raster`` :term:`shape`.

   margin
       The space added in all four directions to the :term:`bounds` of
       some area to improve visual continuity.  For example, a tiling
       or other filling pattern should extend beyond the canvas or
       :term:`region` edges to avoid edge artifacts or gaps.

   outline
       A :term:`shape` or :term:`collection` specifying an area in
       which some function will draw.

   parameter
       A specification for some attribute of a drawing.  A Param (1D) or
       Place (2D) object, or one whose type inherits from them, can
       represent the attribute so that the attribute can vary within
       the drawing, or so that multiple :term:`shapes<shape>` can be
       drawn without having to explicitly generate random values for
       each one.

   point
       A tuple containing the x and y coordinates of a point in 2D
       space.  The units are pixels by default, but can be defined
       with floats.

   region
       A drawing occupying a specified area.  It is generally
       represented as a group :term:`shape` clipped (i.e., contains
       the ``clip`` attribute) by an :term:`outline`.  It is often
       created using either a :term:`bounds` specification or by
       segmenting an :term:`image`.

   segment
       An area of an :term:`image` that is contiguous and visually
       distinct and can form the basis of a :term:`region`.

   shape
       A visual object that is specified by a single SVG element.  It
       is represented by a dictionary with a ``type`` attribute
       specifying the type of shape, and other attributes defining its
       :term:`parameters<parameter>`.

   style
       A visual attribute of a :term:`shape` that is stored in a
       dictionary in the shape's ``style`` attribute.  It usually
       corresponds to an SVG attribute, and any SVG attribute can be
       specified.
