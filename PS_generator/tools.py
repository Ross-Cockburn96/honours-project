import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math
import random
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
    print(f"x is {x}, y is {y}")
    ax.plot(x,y,'ro')
    #only add the valid radius if it is small enough to be of interest/visible and if restricted circle drawing is on
    if not restricted: 
        circle = plt.Circle((x,y),r,color=colour, fill = False, linestyle='--')
        ax.add_artist(circle)
    elif r < parameters.citySizeMax:
        circle = plt.Circle((x,y),r,color=colour, fill = False, linestyle='--')
        ax.add_artist(circle)
    
    
def drawLine(node1, node2, ax, colour='k'):
    x1 = node1.xCoord
    y1 = node1.yCoord
    x2 = node2.xCoord
    y2 = node2.yCoord
    ax.arrow(x1,y1, x2-x1,y2-y1, head_width = .2, head_length=.3, fc=colour,ec=colour, length_includes_head=True)

def drawTrip(trip):
    fig = plt.figure()
    ax = plt.axes()
    ax.set_ylim(0,parameters.citySizeMax)
    ax.set_xlim(0,parameters.citySizeMax)
    prevNode = Node(xCoord = 0, yCoord = 0)
    prevDelivery = None
    maxTravelDistance = trip.deliveries[0].time * parameters.droneSpeed
    drawCircle(prevNode, maxTravelDistance, ax ,restricted = False)
   
    for delivery in  trip.deliveries:
        if prevDelivery != None:
            timeSlotDifference = delivery.time - prevDelivery.time
            maxTravelDistance = (timeSlotDifference * parameters.droneSpeed)
        print(f"printing node {delivery.node}")
        drawCircle(delivery.node, maxTravelDistance, ax, restricted = False)
        drawLine(prevNode, delivery.node, ax)
        prevNode = delivery.node
        prevDelivery = delivery
    plt.show()