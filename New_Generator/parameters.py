import matplotlib.pyplot as plt 
import random


clusterToCitySizeRatio = .0015
rechargingNodetoCitySizeRatio = 0.0020
citySize = 20000 #m^2
dayLength = 28800 #8 hours

seedVal = None
randomGen = random
randomGen.seed(seedVal)
ax = plt.axes()