import os
import algoraphics as ag
import algoraphics.extras as ex

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

#########
# Waves #
#########

# n_waves = 100
# x = []
# for d in (1 + np.arange(n_waves)) / n_waves:
#     wav = ag.wave(start=(200, 200), direction=d * 360, width=d * 20,
#                   period=1 + d * 30, length=1 + d * 180)
#     ag.set_style(wav, 'stroke', (d, 1, 0.5))
#     ag.set_style(wav, 'stroke-width', d * 2)
#     x.append(wav)

# ag.write_SVG(x, w, h, 'svg/shapes1.svg')
# ag.to_PNG('svg/shapes1.svg', 'png/shapes1.png')


######################################
# Wobble (make edges a little messy) #
######################################

x = []
x.append(ag.Circle(c=(100, 100), r=80))
x.append(ag.Line(p1=(200, 30), p2=(250, 170)))
x.append(ag.Line(points=[(300, 30), (330, 170), (350, 90), (370, 160)]))
x.append(ag.Polygon([(30, 230), (30, 370), (170, 230), (170, 370)]))
# x.append(
#     ex.wave(start=(230, 230), direction=45, period=ag.Delta(20, delta=0.1), length=200)
# )
x.append(ag.Spline([(300, 230), (330, 370), (350, 290), (370, 360)]))
ex.wobble(x)

c.add(x)
c.png("png/shapes1.png")
