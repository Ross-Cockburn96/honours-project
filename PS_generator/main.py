
import parameters
import random
import math
from drone import Drone 
from trip import Trip
from delivery import Delivery
from solution import Solution
from problem import Problem 


    
    
   



def populateCustomers():
    customers = [] #each customer has a demand of 1 package 
    #populates list of customers with the deliveries that will satisfy their demands 
    for idx in range(parameters.customers):
        customers.append(Delivery(idx))
    return customers
    
if __name__ == "__main__":
    print("Populating Customers...")
    customers = populateCustomers()
    print("Generating Solution...")
    solution1 = Solution(customers)
    solution1.generate()
    problem = Problem(customers, solution1)
    problem.generate()
    print(solution1)

    