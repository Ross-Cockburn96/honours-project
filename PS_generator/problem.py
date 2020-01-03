import random
import parameters
class Problem: 
    customers = [] 

    def __init__(self, customers, solution=None): 
        self.customers = customers
        self.solution = solution 
    
    def generate(self):
        if self.solution != None: 
            drones = self.solution.drones 
        else: 
            print("Add solution to derive a problem ")
        allTrips = self.solution.getAllTrips() #get list of all trips that are in the solution 
        
        for trip in allTrips: 
            numOfDeliveries = len(trip.deliveries)
            maxWeight = parameters.droneCapacity - (numOfDeliveries -1) #ensure that the max weight is set such that all packages have at least a weight of 1 
            for delivery in trip.deliveries:
                packageWeight = random.randint(1, maxWeight)
                maxWeight -= packageWeight
                delivery.weight = packageWeight
                maxWeight += 1 #once a package is assigned a weight increase the max weight by 1 since there is one less package left to assign 

                
                
