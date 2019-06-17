import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

#####################################
# Objects colored by sampling image #
#####################################

image = ag.open_image("test_images.jpg")
ag.resize_image(image, 800, None)
w, h = image.size
x = ag.tile_canvas(w, h, shape="polygon", tile_size=100)
ag.fill_shapes_from_image(x, image)

c = ag.Canvas(image.width, image.height)
c.add(x)
c.png("png/images1.png")


##################################################
# Image segments colored from image and textured #
##################################################

image = ag.open_image("test_images.jpg")
ag.resize_image(image, 800, None)
w, h = image.size
x = ag.image_regions(image, smoothness=3)
for outline in x:
    color = ag.region_color(outline, image)
    ag.set_style(outline, "fill", color)
ag.add_paper_texture(x)

c.new(x)
c.png("png/images2.png")


####################################
# Image segments with pattern fill #
####################################

image = ag.open_image("test_images.jpg")
ag.resize_image(image, 800, None)
w, h = image.size
x = ag.image_regions(image, smoothness=3)
for i, outline in enumerate(x):
    color = ag.region_color(outline, image)
    maze = ag.Maze_Style_Pipes(rel_thickness=0.6)
    rot = color.value()[0] * 90
    x[i] = ag.fill_maze(outline, spacing=5, style=maze, rotation=rot)
    ag.set_style(x[i]["members"], "fill", color)
    ag.region_background(x[i], ag.contrasting_lightness(color, light_diff=0.2))

c.new(x)
c.png("png/images3.png")
