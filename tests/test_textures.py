import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))
import algoraphics as ag

os.chdir(script_dir)

w = 400
h = 400

######################################################################
# Shadows
######################################################################

d = [dict(command='M', to=(50, 50)),
     dict(command='L', to=(50, 350)),
     dict(command='L', to=(350, 50)),
     dict(command='L', to=(50, 50)),
     dict(command='M', to=(70, 70)),
     dict(command='L', to=(320, 70)),
     dict(command='L', to=(70, 320)),
     dict(command='L', to=(70, 70))]
path = dict(type='path', d=d)
ag.set_style(path, 'fill', "#55CC55")

centers = [(300, 250), (250, 300)]
circles = [ag.circle(c=c, r=50) for c in centers]
ag.set_style(circles[0], 'fill', "#FFDDDD")
ag.set_style(circles[1], 'fill', "#DDDDFF")

x = [path, circles]
# Note that add_shadows adds shadows to the immediate list elements as
# wholes, meaning the top circle should not project a shadow onto the
# one behind it.
ag.add_shadows(x, stdev=20, darkness=0.5)

ag.write_SVG(x, w, h, 'svg/textures1.svg')
ag.to_PNG('svg/textures1.svg', 'png/textures1.png')


######################################################################
# Billowing
######################################################################

outline = ag.circle(c=(120, 120), r=100)
colors = [(0, 1, 0.3), (0.1, 1, 0.5), (0.2, 1, 0.5), (0.4, 1, 0.3)]
x = ag.billow_region(outline, colors, scale=200, gradient_mode='rgb')

outline = ag.circle(c=(280, 280), r=100)
colors = [(0, 1, 0.3), (0.6, 1, 0.3)]
y = ag.billow_region(outline, colors, scale=400, gradient_mode='hsv')

ag.write_SVG([x, y], w, h, 'svg/textures2.svg')
ag.to_PNG('svg/textures2.svg', 'png/textures2.png')


######################################################################
# Paper
######################################################################

x = [ag.rectangle(start=(50, 50), w=300, h=300),
     ag.circle(c=(200, 200), r=150)]
ag.set_style(x[0], 'fill', 'green')
ag.set_style(x[1], 'fill', '#FFCCCC')
ag.add_paper_texture(x)
x = ag.tear_paper_rect(x, (60, 340, 60, 340))

ag.write_SVG(x, w, h, 'svg/textures3.svg')
ag.to_PNG('svg/textures3.svg', 'png/textures3.png')
