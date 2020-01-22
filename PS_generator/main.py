
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
    customers = [] #each customer has a demand of 1 package 
    #populates list of customers with the deliveries that will satisfy their demands 
    for idx in range(parameters.customers):
        customers.append(Node(idx))
    return customers

if __name__ == "__main__":
    
    print("Populating Customers...")
    customers = populateCustomers()
    print("Generating Solution...")
    solution1 = Solution(customers)
    print("finished init")
    solution1.generate()
    print(solution1)
    
    print("Generating Problem...")
    problem = Problem(solution1)
    problem.generate()
    solution1.evaluate(problem)
    print(f"solution1 fitness is {solution1.fitness}")
    print(problem)

    