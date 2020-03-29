import sys
#from context import generatorObjects
from .generators import Generator 
import os 

from generatorObjects.node import CustomerNode, ChargingNode, Node, DepletionPoint, Depot
from generatorObjects.action import ChangeBattery
import matplotlib.pyplot as plt 
from .parameters import Parameters
import random
import new_generator.tools


if __name__ == "__main__": 

    if len(sys.argv) > 1: 
        Parameters.seedVal = int(sys.argv[1])

    generator = Generator(distribution="uniform")  
    generator.generateNodes()
    #problem.generateRechargingStations()
    generator.generateTripsandDrones()
    
    depletionPoints = generator.calculateChargeDepletionPoints()

    rechargeStations = generator.calculateRechargeStations(depletionPoints)
    generator.includeChargingStations(depletionPoints, rechargeStations)
    generator.rechargeStations = rechargeStations
    depletionPoints = generator.calculateChargeDepletionPoints()
    count = 0 
    #check that the distance added to trip from rerouting to charging stations doesn't cause new depletion points
    while len(depletionPoints) > 0:
        count += 1
        print(count)
        chargingStations = [] 
        
        currentDroneBatteries = {}
        for point in depletionPoints: 
            chargingStation = ChargingNode(point.xCoord, point.yCoord)
            chargingStations.append(chargingStation)
        
        generator.includeChargingStations(depletionPoints, chargingStations)
        generator.rechargeStations.extend(chargingStations)

        

        #generator.includeChargingStationsF(depletionPoints, chargingStations)
        depletionPoints = generator.calculateChargeDepletionPoints()

    
    generator.createTimeWindows() 

    generator.createSolutionFile()
    generator.createGenotype()
    generator.createProblemFile()
    


    # plt.sca(parameters.ax)
    # plt.show()
