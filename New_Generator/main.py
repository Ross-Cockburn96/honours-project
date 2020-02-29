from generators import Problem 
import matplotlib.pyplot as plt 
import parameters
import sys
import random
import tools

if __name__ == "__main__": 

    
    if len(sys.argv) > 1: 
        print("setting seed")
        parameters.seedVal = sys.argv[1]

    problem = Problem(noOfNodes = 100, noOfPackages = 50,  distribution="uniform")  
    problem.generateNodes()
    #problem.generateRechargingStations()
    problem.generateTrips()

    plt.sca(parameters.ax)
    plt.show()
