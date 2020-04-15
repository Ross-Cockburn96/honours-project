import matplotlib.pyplot as plt 
import random

class Parameters:
    #don't change
    clusterToCitySizeRatio = .0015
    rechargingNodetoCitySizeRatio = 0.0020
    droneWeightCapacity = 30 #lb
    droneCargoCapacity = 5

    #can change
    citySize = 30000 #m^2
    dayLength = 28800 #s (8 hours)
    noOfPackages = 100
    noOfCustomers = 100
    noOfChargingStations = 30

    #drone properties (can change) 
    droneSpeed = 10 #m/s
    batteryDistance = 40000 #how much distance the drone's current battery has 
    batteryChargingRate = 2 #m/s
    
    seedVal = None
    randomGen = random
    randomGen.seed(seedVal)
    ax = plt.axes()
    timeSlotStandardDev = 60

    #problem parameters can be changed to make problem easier/harder to solve 
    maxDrones = 20
