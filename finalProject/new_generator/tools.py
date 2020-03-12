import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import scipy.stats as stats
import math
from .parameters import Parameters
import random

from generatorObjects.node import Node


def drawTrip(trip, ax=None, show = True, colour = 'k'):
    if ax == None:
        ax = plt.axes() 
        ax.set_ylim(0,Parameters.citySize)
        ax.set_xlim(0,Parameters.citySize)
        ax.add_patch(patches.Rectangle((0,0), Parameters.citySize, Parameters.citySize))
    
    prevAction = trip.actions[0]
    for action in trip.actions[1:]: 
        if prevAction.node.getCoords() != action.node.getCoords(): #don't plot nodes on the same spot
            ax.plot(*prevAction.node.getCoords(),'ro')
            ax.annotate(action.node.id, action.node.getCoords())
            drawLine(prevAction.node, action.node, ax, colour)
        prevAction = action
    
    ax.plot(*trip.actions[-1].node.getCoords(), 'ro')
    if show:
        plt.show()

def drawDroneTrips(drone): 
    plt.cla()
    ax = plt.axes() 
    ax.add_patch(patches.Rectangle((0,0), Parameters.citySize, Parameters.citySize))
    for trip in drone.trips: 
        colourForTrip = (random.uniform(0,1), random.uniform(0,1), random.uniform(0,1))
        drawTrip(trip, ax, False, colourForTrip)
    plt.show()

def drawLine(node1, node2, ax, colour = 'k'):
    x1, y1 = node1.getCoords()
    x2, y2 = node2.getCoords()

    xdata = np.array([x1,x2])
    ydata = np.array([y1,y2])

    #calculate unit vector 
    x = xdata[1] - xdata[0] 
    y = ydata[1] - ydata[0] 
    magVector = math.sqrt(x**2 + y**2)
    unitX = x/magVector
    unitY = y/magVector

    #find midpoint 
    midx = sum(xdata)/2
    midy = sum(ydata)/2

    #insert midpoint and (midpoint + small value) to plotting arrays so arrow can be annotated at the coords
    xdata = np.insert(xdata, 1, (midx, midx + (unitX*3))) 
    ydata = np.insert(ydata, 1, (midy, midy + (unitY*3)))

    line = ax.plot(xdata, ydata, color = colour)[0] #plot function returns a list of lines but there is only ever 1 line 
    add_arrow(line, ax,color = colour)

def add_arrow(line, ax, position=None, direction='right', size=15, color=None): #taken from https://stackoverflow.com/questions/34017866/arrow-on-a-line-plot-with-matplotlib
    """
    add an arrow to a line.
    line:       Line2D object
    position:   x-position of the arrow. If None, mean of xdata is taken
    direction:  'left' or 'right'
    size:       size of the arrow in fontsize points
    color:      if None, line color is taken.
    """
    if color is None:
        color = line.get_color()

    #get point data from line
    xdata = line.get_xdata()
    ydata = line.get_ydata()


    if position is None:
        position = xdata.mean()

    #find closest index
    start_ind = np.argmin(np.absolute(xdata - position))
    
    if direction == 'right':
        end_ind = start_ind + 1
    else:
        end_ind = start_ind - 1
    ax.annotate('',
        xytext=(xdata[start_ind], ydata[start_ind]),
        xy=(xdata[end_ind], ydata[end_ind]),
        arrowprops=dict(arrowstyle="->", color=color),
        size=size
    )

def plotValues(values):
    values = np.array(values)
    rangeVal = max(values) - min(values)
    numberOfInstances = len(values)
    numIntervals = int(math.sqrt(numberOfInstances))
    widthIntervals = rangeVal/numIntervals
    bins = []

    binValue = min(values)
    for val in range(0, numberOfInstances, numIntervals):
        bins.append(binValue)
        binValue += widthIntervals 
    bins[-1] = bins[-2] + widthIntervals 

    plt.hist(values, bins = bins)
    plt.show()