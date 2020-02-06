
import parameters
import random
import math
from drone import Drone 
from trip import Trip
from delivery import Delivery
from solution import Solution
from problem import Problem 
from Node import Node
import tools 
import sys 


def populateCustomers():
    customers = [] #each customer is a node which has a demand of 1 specific package 

    '''
    Populates list of customers with the deliveries that will satisfy their demands.
    Does not start from 0 because 0 is reserved for depot node
    '''
    for idx in range(1,parameters.customers + 1): 
        customers.append(Node(idx))
    return customers

if __name__ == "__main__":
    if len(sys.argv) > 1: 
        parameters.seed = sys.argv[1] #takes the seed argument from command line 


    # import matplotlib.pyplot as plt
    # #fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.set_ylim(0,6)
    # ax.set_xlim(0,6)
    # #tools.drawCircle(5,2,1, ax)
    # #tools.drawCircle(3,2,2, ax)
    # n1 = Node(xCoord = 5, yCoord = 2)
    # n2 = Node(xCoord = 3, yCoord =2)
    #tools.drawLine(n1,n2,ax)
    #plt.show()
    # import numpy as np

    # numberOfinstances = 100000
    # mu = 0
    # variance = 1
    # sigma = math.sqrt(variance)
    
    # values = np.empty(numberOfinstances)
    # for i in range(numberOfinstances):
    #     values[i] = random.gauss(0, parameters.timeSlotStandardDev)
    # #tools.plotValues(values)

    # values2 = np.empty(numberOfinstances)
    # for i in range(numberOfinstances):
    #     mean = random.randint(-parameters.dayLength/4, parameters.dayLength/4)
    #     values2[i] = random.gauss(mean, parameters.timeSlotStandardDev)
    
    # values3 = np.empty(numberOfinstances)
    # for i in range(numberOfinstances):
    #     values3[i] = abs(random.gauss(0, parameters.timeSlotStandardDev))
    
    # values4 = np.empty(numberOfinstances)
    # for i in range(numberOfinstances):
    #     mean = random.randint(0, parameters.dayLength/4)
    #     values4[i] = abs(random.gauss(mean, parameters.timeSlotStandardDev)) + 10
    # tools.plotManyHists(values, values2, values3, values4) #doesn't work because plots can only be 1 or 2 


    # rangeVal = max(values) - min(values)
    # numIntervals = int(math.sqrt(numberOfinstances))
    # widthIntervals = rangeVal/numIntervals
    # bins = [] 
    # binValue = min(values)
    # for val in range(0,numberOfinstances, numIntervals):
    #     bins.append(binValue)
    #     binValue += widthIntervals 
    # bins[-1] = bins[-2] + widthIntervals
    # print(len(bins))
    # for val in bins: 
    #     print(val)
   
    # plt.hist(values, bins =bins)
    # plt.show()
    # plt.style.use('ggplot')
    # plt.hist(values, bins=bins)
    # plt.show()
   



    print("Populating Customers...")
    customers = populateCustomers()
    print("Generating Solution...")
    solution1 = Solution(customers)
    solution1.generate()
    print(solution1)
    
    print("Generating Problem...")
    problem = Problem(solution1)
    problem.generate()
    problem.writeToFile()
    solution1.evaluate(problem)
    print(f"solution1 fitness is {solution1.fitness}")

    solution2 = Solution(customers)
    solution2.generate()
    solution2.evaluate(problem)

    print(f"solution2 fitness is {solution2.fitness}")
    
    print(problem)

    