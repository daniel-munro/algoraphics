import os
import algoraphics as ag
import algoraphics.extras as ex

os.chdir(os.path.dirname(os.path.abspath(__file__)))

#####################################
# Objects colored by sampling image #
#####################################

image = ex.open_image("test_images.jpg")
ex.resize_image(image, 800, None)
w, h = image.size
x = ex.tile_canvas(w, h, shape="polygon", tile_size=100)
ex.fill_shapes_from_image(x, image)

c = ag.Canvas(image.width, image.height)
c.add(x)
c.png("png/images1.png")


#####################################
# Image segments colored from image #
#####################################

image = ex.open_image("test_images.jpg")
ex.resize_image(image, 800, None)
w, h = image.size
x = ex.image_regions(image, smoothness=3)
for outline in x:
    color = ex.region_color(outline, image)
    ag.set_style(outline, "fill", color)

c.new(x)
c.png("png/images2.png")


####################################
# Image segments with pattern fill #
####################################

image = ex.open_image("test_images.jpg")
ex.resize_image(image, 800, None)
w, h = image.size
x = ex.image_regions(image, smoothness=3)
for i, outline in enumerate(x):
    color = ex.region_color(outline, image)
    maze = ex.Maze_Style_Pipes(rel_thickness=0.6)
    rot = color.hue.state() * 90
    x[i] = ex.fill_maze(outline, spacing=5, style=maze, rotation=rot)
    ag.set_style(x[i].members, "fill", color)
    ag.region_background(x[i], ex.contrasting_lightness(color, light_diff=0.2))

c.new(x)
c.png("png/images3.png")
