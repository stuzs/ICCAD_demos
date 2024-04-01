#!/usr/bin/env python
"""The program reads in a binary image of metal jog, down-samples
the image and discretizes the metal strip into a mesh of resistors.
Then it calls a DC simulator to analyze mesh node voltages and
from the voltage outputs calculates current out-flowing from each node.
A mesh voltage graph and a mesh current density graph are then plotted.
"""

from PIL import Image
import numpy
import math
import os
import re
import matplotlib.pyplot as plt

# I drew two images by GIMP, but other image tool should be fine
image = Image.open('metal-jog.png')
#image = Image.open('metal-slot.bmp')
print(image.format, image.size, image.mode)

img_xsize, img_ysize = image.size
imgData = numpy.asarray(image)
# check the image data representation, most likely as n-bit integers
print(imgData)

grid_size = 4  # this number defines the coarseness of resistor mesh
mesh_xsize = math.ceil(img_xsize / grid_size)  # mesh X/Y down-sized
mesh_ysize = math.ceil(img_ysize / grid_size)  # ysize for mesh row number
meshDots = numpy.zeros([mesh_ysize, mesh_xsize])  # dot marks metal area

# down-sample input image to fill the mesh array
n = 0
for j in range(0, img_ysize, grid_size):
    m = 0
    for i in range(0, img_xsize, grid_size):
        if imgData[j][i] != 0:
            meshDots[n][m] = 1
        m += 1
    n += 1
print(meshDots)

# create a SPICE compatible netlist for DC simulation
f = open("./resmesh.spice", "w")

# generate circuit title and voltage sources connecting the metal.
# note that the current always goes from northwest to southeast.
print("* A right angle metal strip in mesh\n\
* The metal strip is discretized into a large resistor mesh\n\
* by running a Python program to process a binary image of\n\
* the metal shape. The current goes from northwest to southeast.", file=f)
print("Vin n_0_0 gnd 1", file=f)
print("Vgnd n_%d_%d gnd 0" % (mesh_xsize-1, mesh_ysize-1), file=f)

# generate resistors row by row horizontally then vertically.
# if a neighbor on next row is also 1, generate a vertical resistor between.
# A fixed value 0.01-Ohm resistance is assumed tentatively.
for j in range(mesh_ysize):
    for i in range(mesh_xsize):
        if meshDots[j][i] == 1:
            if i < mesh_xsize-1 and meshDots[j][i+1] == 1:
                print("Rh_%d_%d n_%d_%d n_%d_%d 0.01"
                      % (i, j, i, j, i+1, j), file=f)
            if j < mesh_ysize-1 and meshDots[j+1][i] == 1:
                print("Rv_%d_%d n_%d_%d n_%d_%d 0.01"
                      % (i, j, i, j, i, j+1), file=f)

# close the SPICE compatible netlist
f.close()

# run circuit simulator (SPICE) for all node voltages
ret_code = os.system("python ../iccad_mna.py resmesh.spice > meshvolt.out")
if ret_code != 0:
    exit(ret_code)

# after running SPICE, read back SPICE outputs and sum the out-flowing
# currents from each node and plot this sum (current densities) to
# another image.

# read file meshvolt.out, then match SPICE outputs using Regular Expressions
meshVolt = numpy.zeros([mesh_ysize, mesh_xsize])
with open("./meshvolt.out") as fmv:
    for line in fmv.readlines():
        if re.match('^node N_\d+_\d+', line):
            node_args = re.split(' ', line)
            nl = re.findall('\d+', node_args[1])
            volt = re.search('[^V]+', node_args[2])
            meshVolt[int(nl[1])][int(nl[0])] = volt.group()

# 'with' automatically takes care of closing file after its block
# fmv.close()


plt.subplot(211)
plt.imshow(meshVolt, cmap='inferno')

meshAmpre = numpy.zeros([mesh_ysize, mesh_xsize])
for j in range(mesh_ysize):
    for i in range(mesh_xsize):
        if meshDots[j][i] == 1:
            outCurrent = 0
            if i < mesh_xsize-1 and meshDots[j][i+1] == 1:
                outCurrent += (meshVolt[j][i] - meshVolt[j][i+1]) / 0.01
            if j < mesh_ysize-1 and meshDots[j+1][i] == 1:
                outCurrent += (meshVolt[j][i] - meshVolt[j+1][i]) / 0.01
            meshAmpre[j][i] = outCurrent

plt.subplot(212)
plt.imshow(meshAmpre, cmap='plasma')
plt.show()
