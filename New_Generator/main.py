from generators import Problem 
import matplotlib.pyplot as plt 
import parameters
import sys
import random
import tools

if __name__ == "__main__": 

    
    if len(sys.argv) > 1: 
        print("setting seed")
        parameters.seedVal = int(sys.argv[1])

    problem = Problem(noOfNodes = 100, noOfPackages = 400,  distribution="uniform")  
    problem.generateNodes()
    #problem.generateRechargingStations()
    problem.generateTripsandDrones()
    depletionPoints = problem.calculateChargeDepletionPoints()
    rechargeStations = problem.calculateRechargeStations(depletionPoints)
    problem.includeChargingStations(depletionPoints, rechargeStations)

    plt.sca(parameters.ax)
    plt.show()
