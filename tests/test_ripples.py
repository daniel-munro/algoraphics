import os
import algoraphics as ag

os.chdir(os.path.dirname(os.path.abspath(__file__)))

c = ag.Canvas(400, 400)

###########################
# Object-avoiding ripples #
###########################

circ = ag.points_on_arc(
    center=(200, 200), radius=100, theta_start=0, theta_end=360, spacing=10
)
x = ag.ripple_canvas(c.width, c.height, spacing=10, existing_pts=circ)

c.add(x)
c.png("png/ripples1.png")


##########################
# More irregular ripples #
##########################

trans_probs = dict(
    S=dict(X=1),
    R=dict(R=0.9, L=0.05, X=0.05),
    L=dict(L=0.9, R=0.05, X=0.05),
    X=dict(R=0.5, L=0.5),
)
circ = ag.points_on_arc(
    center=(200, 200), radius=100, theta_start=0, theta_end=360, spacing=10
)
x = ag.ripple_canvas(
    c.width, c.height, spacing=10, trans_probs=trans_probs, existing_pts=circ
)

c.new(x)
c.png("png/ripples2.png")
