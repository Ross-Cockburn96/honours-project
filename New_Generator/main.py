from generators import Problem 
import matplotlib.pyplot as plt 
import parameters

if __name__ == "__main__": 
    problem = Problem(100, 50,  "uniform")
    problem.generateNodes()
    problem.generateRechargingStations()

    plt.sca(parameters.ax)
    plt.show()
