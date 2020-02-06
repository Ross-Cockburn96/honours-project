import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import scipy.stats as stats
import math
import parameters
from Node import Node

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

def plotManyHists(*args):
    fig = plt.figure()
    sets = list(args)
    print(len(sets))
    for idx, data in enumerate(sets): 
        ax = fig.add_subplot(len(sets),1, idx+1)
    # ax1 = fig.add_subplot(2,1,1)
    # ax2 = fig.add_subplot(2,1,2)
        values = np.array(data)
    # values1 = np.array(values1)
    # values2 = np.array(values2)

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

        ax.hist(values, bins = bins)
   

    plt.show()

def drawCircle(node,r,ax, colour='k', restricted=True):
    x = node.xCoord
    y = node.yCoord
    print(f"x is {x}, y is {y}, r is {r}")
    ax.plot(x,y,'ro')
    #only add the valid radius if it is small enough to be of interest/visible and if restricted circle drawing is on
    if not restricted: 
        print("drawing circle")
        circle = plt.Circle((x,y),r,color=colour, fill = False, linestyle='--')
        ax.add_artist(circle)
    elif r < parameters.citySizeMax:
        circle = plt.Circle((x,y),r,color=colour, fill = False, linestyle='--')
        ax.add_artist(circle)
    else:
        print("not drawing circle")
    
def drawLine(node1, node2, ax, colour='k'):
    x1 = node1.xCoord
    y1 = node1.yCoord
    x2 = node2.xCoord
    y2 = node2.yCoord
    #ax.arrow(x1,y1, x2-x1,y2-y1, head_width = 500, head_length=500, fc=colour,ec=colour, length_includes_head=True)
    line = ax.plot((x1,x2),(y1, y2), colour)[0]
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


    xdata = line.get_xdata()
    ydata = line.get_ydata()

    
    if position is None:
        position = xdata.mean()
        print(f"xData is {xdata} and position is {position}")
    # find closest index
    start_ind = np.argmin(np.absolute(xdata - position))
    print(f"start index is {start_ind}")
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




def drawTrip(trip):
    fig = plt.figure()
    ax = plt.axes()
    ax.set_ylim(0,parameters.citySizeMax)
    ax.set_xlim(0,parameters.citySizeMax)
    ax.add_patch(patches.Rectangle((0,0), parameters.citySizeMax, parameters.citySizeMax))
    depot = Node(xCoord = 0, yCoord = 0)

    #iterates through trip deliveries and draws the previous node and potential delivery circle based on the current node 
    for delivery in trip.deliveries:
        if delivery.prevDelivery == None: #if this is the first delivery of trip then use depot as previous node 
            maxTravelDistance = delivery.time * parameters.droneSpeed
            drawCircle(depot, maxTravelDistance, ax, restricted = False)
            drawLine(depot, delivery.node, ax) #draw line from depot
        else:
            timeSlotDifference = delivery.time - delivery.prevDelivery.time
            maxTravelDistance = timeSlotDifference * parameters.droneSpeed
            drawLine(delivery.prevDelivery.node, delivery.node, ax)
            drawCircle(delivery.prevDelivery.node, maxTravelDistance, ax, restricted = False) #the max distance of this should be the next node not this one 
    
    x,y = trip.deliveries[-1].node.getCoords()
    ax.plot(x,y,'ro') #plot the last node 
    drawLine(trip.deliveries[-2].node, trip.deliveries[-1].node, ax) #draw line from 2nd last node to last node 

    drawLine(trip.deliveries[-1].node, depot, ax) #draw line from last node to depot

    plt.show()