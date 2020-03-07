import sys
sys.path.insert(0, "..")
from generators import Generator 
from generatorObjects.node import CustomerNode, ChargingNode, Node, DepletionPoint, Depot
import matplotlib.pyplot as plt 
import parameters
import random
import tools

if __name__ == "__main__": 

    
    if len(sys.argv) > 1: 
        print("setting seed")
        parameters.seedVal = int(sys.argv[1])

    generator = Generator(noOfNodes = 100, noOfPackages = 100,  distribution="uniform")  
    generator.generateNodes()
    #problem.generateRechargingStations()
    generator.generateTripsandDrones()
    
    depletionPoints = generator.calculateChargeDepletionPoints()

    rechargeStations = generator.calculateRechargeStations(depletionPoints)
    generator.includeChargingStations(depletionPoints, rechargeStations)
    generator.rechargeStations = rechargeStations
    depletionPoints = generator.calculateChargeDepletionPoints()

    #check that the distance added to trip from rerouting to charging stations doesn't cause new depletion points
    while len(depletionPoints) > 0:
        chargingStations = [] 
        for point in depletionPoints: 
            chargingStations.append(ChargingNode(point.xCoord, point.yCoord))
        generator.rechargeStations.extend(chargingStations)
        generator.includeChargingStations(depletionPoints, chargingStations)
        depletionPoints = generator.calculateChargeDepletionPoints()
  
    
    generator.createTimeWindows() 

    generator.createSolutionFile()
    generator.createProblemFile()
    
    # plt.sca(parameters.ax)
    # plt.show()
