from generatorObjects.node import Depot, CustomerNode, ChargingNode
from generatorObjects.battery import Battery
from generatorObjects.package import Package


'''
Input: {List}
List of the elements contained in the problem file and rebuilds the data structures from the elements 

Returns: {Tuple}
    list of nodes  
    list of packages
'''
def buildNodes(problemElements): 

    problemCountIdx = 7 #first 5 elements are problem characteristics, 6 and 7 are always 0 for depot coordinates so set index to 8th element (idx 7) 
    depot = Depot()
    
    nodes = []
    packages = []
    nodes.append(depot)

    numberBatteriesInDepot = problemElements[problemCountIdx]
    numberOfCustomers = problemElements[2]
    numberOfPackages = problemElements[3]
    numberOfRechargeStations = problemElements[4]
    problemCountIdx += 1

    #extract number of batteries initialised to depot
    for _ in range(numberBatteriesInDepot):
        Depot.batteriesHeld.append(Battery.createWithID(problemElements[problemCountIdx]))
        problemCountIdx += 1

    #extract customer nodes from problem file
    for _ in range(numberOfCustomers): 
        customerNode = CustomerNode.rebuild(*problemElements[problemCountIdx:problemCountIdx+4])
        nodes.append(customerNode)
        problemCountIdx += 4

    #extract package data from problem file 
    for _ in range(numberOfPackages):
        package = Package(problemElements[problemCountIdx])
        problemCountIdx += 1
        package.weight = problemElements[problemCountIdx]
        problemCountIdx += 1
        package.destination = problemElements[problemCountIdx]
        problemCountIdx += 1
        packages.append(package)
    
    #extract recharging station from problem file 
    for _ in range(numberOfRechargeStations):
        chargeStation = ChargingNode(*problemElements[problemCountIdx:problemCountIdx+2])
        problemCountIdx += 2
        numberOfBatteries = problemElements[problemCountIdx] #the number of batteries initialised at this recharging station
        problemCountIdx += 1
        chargeStation.capacity = numberOfBatteries
        chargeStation.batteriesHeld = [Battery.createWithID(batteryID) for batteryID in problemElements[problemCountIdx:problemCountIdx + numberOfBatteries]]
        nodes.append(chargeStation)
        problemCountIdx += numberOfBatteries

    return (nodes,packages)