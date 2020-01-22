
import parameters
import random
import math
from drone import Drone 
from trip import Trip
from delivery import Delivery
from solution import Solution
from problem import Problem 
from Node import Node
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
    
    print("Populating Customers...")
    customers = populateCustomers()
    print("Generating Solution...")
    solution1 = Solution(customers)
    solution1.generate()
    print(solution1)
    
    print("Generating Problem...")
    problem = Problem(solution1)
    problem.generate()
    solution1.evaluate(problem)
    print(f"solution1 fitness is {solution1.fitness}")

    solution2 = Solution(customers)
    solution2.generate()
    solution2.evaluate(problem)

    print(f"solution2 fitness is {solution2.fitness}")
    
    print(problem)

    