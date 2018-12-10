import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

######################################################################
# Objects colored by sampling image
######################################################################

image = ag.open_image("test_images.jpg")
ag.resize_image(image, 800, None)
w, h = image.size
x = ag.tile_canvas(w, h, shape='polygon', tile_size=100)
ag.fill_shapes_from_image(x, image)

ag.write_SVG(x, w, h, 'svg/images1.svg')
ag.to_PNG('svg/images1.svg', 'png/images1.png')


######################################################################
# Image segments colored from image and textured
######################################################################

image = ag.open_image("test_images.jpg")
ag.resize_image(image, 800, None)
w, h = image.size
x = ag.image_regions(image, smoothness=3)
for outline in x:
    color = ag.region_color(outline, image)
    ag.set_style(outline, 'fill', color)
ag.add_paper_texture(x)

ag.write_SVG(x, w, h, 'svg/images2.svg')
ag.to_PNG('svg/images2.svg', 'png/images2.png')


######################################################################
# Image segments with pattern fill
######################################################################

image = ag.open_image("test_images.jpg")
ag.resize_image(image, 800, None)
w, h = image.size
x = ag.image_regions(image, smoothness=3)
for i, outline in enumerate(x):
    color = ag.region_color(outline, image)
    maze = ag.Maze_Style_Pipes(rel_thickness=0.6)
    x[i] = ag.fill_maze_hue_rotate(outline, spacing=5, style=maze,
                                   color=color)
    ag.region_background(x[i], ag.contrasting_lightness(color, light_diff=0.2))
    ag.set_style(outline, 'fill', color)
ag.add_paper_texture(x)

ag.write_SVG(x, w, h, 'svg/images3.svg')
ag.to_PNG('svg/images3.svg', 'png/images3.png')
