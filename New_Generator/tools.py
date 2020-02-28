import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import scipy.stats as stats
import math
import parameters
import random

from generatorObjects.node import Node

def drawTrip(trip, ax=None, show = True, colour = 'k'):
    if ax == None:
        ax = plt.axes() 
        ax.set_ylim(0,parameters.citySizeMax)
        ax.set_xlim(0,parameters.citySizeMax)
        ax.add_patch(patches.Rectangle((0,0), parameters.citySizeMax, parameters.citySizeMax))
    
    for action in trip.actions: 
        if action.prevAction:
            pass