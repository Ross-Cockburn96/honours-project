import matplotlib.pyplot as plt 
import random

#don't change
clusterToCitySizeRatio = .0015
rechargingNodetoCitySizeRatio = 0.0020
droneWeightCapacity = 30 #lb
droneCargoCapacity = 5

#can change
citySize = 20000 #m^2
dayLength = 28800 #s (8 hours)


#drone properties (can change) 
droneSpeed = 10 #m/s
batteryDistance = 20000 #how much distance the drone's current battery has 



seedVal = None
randomGen = random
randomGen.seed(seedVal)
ax = plt.axes()
timeSlotStandardDev = 60

#problem parameters can be changed to make problem easier/harder to solve 
maxDrones = 20
