
from new_generator.parameters import Parameters 

'''
Takes a solution in the form as drone objects and returns a list of its raw elements in the format that can be written to solution files 
'''
def phenotype(drones): 
    outputElements = [] 
    outputElements.append(len(drones))
    for drone in drones: 
        #tools.drawDroneTrips(drone)
        outputElements.append(len(drone.trips))
        for trip in drone.trips: 
            outputElements.append(len(trip.actions))
            for action in trip.actions: 
                outputElements.append(action.node.id)
                #if action a deliver action add id of package delivered to solution file 
                if (action.node.id) > 0 and (action.node.id <= Parameters.noOfCustomers):
                    outputElements.append(action.package.id)
                elif "ChangeBattery" in str(type(action)): 
                    outputElements.append(action.batteryDropped)
                    outputElements.append(action.batterySelected)
    return [str(e) for e in outputElements]


