import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Splatter text
######################################################################

x = []
color = ag.Color(hue=ag.Uniform(0, 0.15), sat=0.8, li=0.5)

y = ag.splatter_text('ABCDEFG', height=50, spread=2, density=2,
                     min_size=1, max_size=3, color=color)
ag.reposition(y, (w / 2, h - 50), 'center', 'top')
x.append(y)

y = ag.splatter_text('HIJKLM', height=50, spread=2, density=2,
                     min_size=1, max_size=3, color=color)
ag.reposition(y, (w / 2, h - 150), 'center', 'top')
x.append(y)

y = ag.splatter_text('0123456789', height=50, spread=2, density=2,
                     min_size=1, max_size=3, color=color)
ag.reposition(y, (w / 2, h - 250), 'center', 'top')
x.append(y)

ag.write_SVG(x, w, h, 'svg/text1.svg')
ag.to_PNG('svg/text1.svg', 'png/text1.png')


######################################################################
# Double dots text
######################################################################

x = []

y = ag.double_dots_text('NOPQRST', height=40)
ag.reposition(y, (w / 2, h - 50), 'center', 'top')
x.append(y)

y = ag.double_dots_text('UVWXYZ', height=40, top_color='#FF8888',
                        bottom_color='#555555')
ag.reposition(y, (w / 2, h - 150), 'center', 'top')
x.append(y)

y = ag.double_dots_text(".,!?:;'\"/", height=40, top_color='#FF8888',
                        bottom_color='#555555')
ag.reposition(y, (w / 2, h - 250), 'center', 'top')
x.append(y)

ag.write_SVG(x, w, h, 'svg/text2.svg')
ag.to_PNG('svg/text2.svg', 'png/text2.png')


######################################################################
# Hazy text
######################################################################

x = []

y = ag.hazy_text('abcdefg', height=50, spread=10, density=3,
                 min_size=0.5, max_size=2, color='green')
ag.reposition(y, (w / 2, h - 100), 'center', 'top')
x.append(y)

y = ag.hazy_text('hijklm', height=50, spread=10, density=3,
                 min_size=0.5, max_size=2, color='green')
ag.reposition(y, (w / 2, h - 250), 'center', 'top')
x.append(y)

ag.write_SVG(x, w, h, 'svg/text3.svg')
ag.to_PNG('svg/text3.svg', 'png/text3.png')


######################################################################
# Squiggle text
######################################################################

x = []

y = ag.squiggle_text('nopqrst', height=60, spread=10, density=1)
ag.reposition(y, (w / 2, h - 100), 'center', 'top')
x.append(y)

y = ag.squiggle_text('uvwxyz', height=60, spread=10, density=1)
ag.reposition(y, (w / 2, h - 250), 'center', 'top')
x.append(y)

ag.write_SVG(x, w, h, 'svg/text4.svg')
ag.to_PNG('svg/text4.svg', 'png/text4.png')


######################################################################
# Caption (SVG text)
######################################################################

w, h = 400, 100
x = ag.caption("SVG text.", anchor=(w-20, 20))

ag.write_SVG(x, w, h, 'svg/text5.svg')
ag.to_PNG('svg/text5.svg', 'png/text5.png')
