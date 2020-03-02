from generators import Generator 
import matplotlib.pyplot as plt 
import parameters
import sys
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
    generator.createTimeWindows() 

    generator.createSolutionFile()
    generator.createProblemFile()
    
    plt.sca(parameters.ax)
    plt.show()
