import os
import algoraphics as ag
import algoraphics.extras as ex

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

############################
# Animated spot fill (GIF) #
############################


def frame1():
    outline = ag.circle(c=(200, 200), r=180)
    color = ag.Color(
        hue=ag.Uniform(min=0.6, max=0.8), sat=0.7, li=ag.Uniform(min=0.5, max=0.7)
    )
    x = ex.fill_spots(outline, spacing=30)
    ag.set_style(x, "fill", color)
    c.new(x)
    return c


ag.gif(frame1, seconds=2, fps=12, file_name="png/svg1.gif")


##############################
# Animated spot fill (video) #
##############################


def frame2():
    outline = ag.circle(c=(200, 200), r=180)
    color = ag.Color(
        hue=ag.Uniform(min=0.6, max=0.8), sat=0.7, li=ag.Uniform(min=0.5, max=0.7)
    )
    x = ex.fill_spots(outline, spacing=30)
    ag.set_style(x, "fill", color)
    c.new(x)
    return c


ag.video(frame2, seconds=2, fps=12, file_name="png/svg2.mp4")


#####################################
# Time-dependent animated spot fill #
#####################################


def frame3(t):
    outline = ag.circle(c=(200, 200), r=180)
    color = ag.Color(hue=ag.Uniform(min=0.6, max=0.8), sat=0.7, li=1 - 0.4 * abs(1 - t))
    x = ex.fill_spots(outline, spacing=30)
    ag.set_style(x, "fill", color)
    c.new(x)
    return c


ag.gif(frame3, seconds=2, fps=12, file_name="png/svg3.gif")
