import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

w, h = 400, 400
c = ag.Canvas(w, h)

#################
# Splatter text #
#################

color = ag.Color(hue=ag.Uniform(0, 0.15), sat=0.8, li=0.5)

x1 = ag.splatter_text(
    "ABCDEFG", height=50, spread=2, density=2, min_size=1, max_size=3, color=color
)
ag.reposition(x1, (w / 2, h - 50), "center", "top")

x2 = ag.splatter_text(
    "HIJKLM", height=50, spread=2, density=2, min_size=1, max_size=3, color=color
)
ag.reposition(x2, (w / 2, h - 150), "center", "top")

x3 = ag.splatter_text(
    "0123456789", height=50, spread=2, density=2, min_size=1, max_size=3, color=color
)
ag.reposition(x3, (w / 2, h - 250), "center", "top")

c.add(x1, x2, x3)
c.png("png/text1.png")


####################
# Double dots text #
####################

x1 = ag.double_dots_text("NOPQRST", height=40)
ag.reposition(x1, (w / 2, h - 50), "center", "top")

x2 = ag.double_dots_text(
    "UVWXYZ", height=40, top_color="#FF8888", bottom_color="#555555"
)
ag.reposition(x2, (w / 2, h - 150), "center", "top")

x3 = ag.double_dots_text(
    ".,!?:;'\"/", height=40, top_color="#FF8888", bottom_color="#555555"
)
ag.reposition(x3, (w / 2, h - 250), "center", "top")

c.new(x1, x2, x3)
c.png("png/text2.png")


#############
# Hazy text #
#############

x1 = ag.hazy_text(
    "abcdefg", height=50, spread=10, density=3, min_size=0.5, max_size=2, color="green"
)
ag.reposition(x1, (w / 2, h - 100), "center", "top")

x2 = ag.hazy_text(
    "hijklm", height=50, spread=10, density=3, min_size=0.5, max_size=2, color="green"
)
ag.reposition(x2, (w / 2, h - 250), "center", "top")

c.new(x1, x2)
c.png("png/text3.png")


#################
# Squiggle text #
#################

x1 = ag.squiggle_text("nopqrst", height=60, spread=10, density=1)
ag.reposition(x1, (w / 2, h - 100), "center", "top")

x2 = ag.squiggle_text("uvwxyz", height=60, spread=10, density=1)
ag.reposition(x2, (w / 2, h - 250), "center", "top")

c.new(x1, x2)
c.png("png/text4.png")


######################
# Caption (SVG text) #
######################

w, h = 400, 100
c = ag.Canvas(w, h)
x = ag.caption("SVG text.", anchor=(w - 20, 20))

c.add(x)
c.png("png/text5.png")
