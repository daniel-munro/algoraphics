# convert -dither None $1_*.svg -clone 0 -morph 5 -delete -1 $1.gif

convert -dither None -delay 5 $1_*.svg -clone 0 -morph 1 -delete -1 $1.gif

# convert -dither None $1_*.svg $1.gif
