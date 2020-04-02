from generatorObjects.drone import Drone
from generatorObjects.trip import Trip
from generatorObjects.action import Delivery, ChangeBattery, AtDepot
from generatorObjects.battery import Battery
'''
Inputs: {List}, int, {List}, {List}
List of the elements contained the solution file and rebuilds the data structures from the elements
number of customers in the problem
List of the nodes contained in the problem file 
List of the packages contained in the problem file

Returns: {List}
List of drones with their underlying datastructures (such as trips) populated
'''

def buildObjects(solutionElements, numberOfCustomers, nodes, packages):
    drones = []
    solutionElements = [int(e) for e in solutionElements]
    solutionCountIdx = 1 #this index gives the number of trips in the first drone 
    #loops through the drones
    while solutionCountIdx < len(solutionElements):
        droneTrips = int(solutionElements[solutionCountIdx])
        solutionCountIdx += 1

        #loops through the trips of the drone
        trips = []
        for _ in range(droneTrips):
            tripActions = int(solutionElements[solutionCountIdx])
            solutionCountIdx += 1

            actions = []
            #loops through the actions of a trip
            for _ in range(tripActions): 
                element = int(solutionElements[solutionCountIdx])
                if element == 0: 
                    action = AtDepot()
                    solutionCountIdx += 1
                elif element > numberOfCustomers: 
                    action = ChangeBattery(nodes[element], Battery.createWithID(solutionElements[solutionCountIdx + 1]), Battery.createWithID(solutionElements[solutionCountIdx + 2]))
                    solutionCountIdx += 3
                else: 
                    action = Delivery(nodes[element], packages[solutionElements[solutionCountIdx + 1]-1]) #package ids start at 1 but package list index starts at 0 so minus one from the id in the solution to get correct package
                    solutionCountIdx +=2
                actions.append(action)
            trips.append(Trip(*actions))
        drones.append(Drone(*trips))
    return drones